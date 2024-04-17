#include "Dps422.h"

using namespace dps;
using namespace dps422;

////////   public  /////////

int16_t Dps422::measureBothOnce(float &prs, float &temp)
{
	measureBothOnce(prs, temp, m_prsOsr, m_tempOsr);
}

int16_t Dps422::measureBothOnce(float &prs, float &temp, uint8_t prs_osr, uint8_t temp_osr)
{
	if (prs_osr != m_prsOsr)
	{
		if (configPressure(0U, prs_osr))
		{
			return DPS__FAIL_UNKNOWN;
		}
	}

	if (temp_osr != m_tempOsr)
	{
		if (configPressure(0U, temp_osr))
		{
			return DPS__FAIL_UNKNOWN;
		}
	}

	setOpMode(CMD_BOTH);
	delay(((calcBusyTime(0U, m_tempOsr) + calcBusyTime(0U, m_prsOsr)) / DPS__BUSYTIME_SCALING));
	// config_registers defined in namespace dps
	int16_t rdy = readByteBitfield(config_registers[PRS_RDY]) & readByteBitfield(config_registers[TEMP_RDY]);
	switch (rdy)
	{
	case DPS__FAIL_UNKNOWN: //could not read ready flag
		return DPS__FAIL_UNKNOWN;
	case 0: //ready flag not set, measurement still in progress
		standby();
		return DPS__FAIL_UNFINISHED;
	case 1: //measurement ready, expected case
		m_opMode = IDLE;
		int32_t raw_temp;
		int32_t raw_psr;
		if (getRawResult(&raw_temp, registerBlocks[TEMP]) || getRawResult(&raw_psr, registerBlocks[PRS]))
			return DPS__FAIL_UNKNOWN;
		prs = calcPressure(raw_psr);
		temp = calcTemp(raw_temp);
		return DPS__SUCCEEDED;
	}
}

int16_t Dps422::getContResults(float *tempBuffer,
							   uint8_t &tempCount,
							   float *prsBuffer,
							   uint8_t &prsCount)
{
	return DpsClass::getContResults(tempBuffer, tempCount, prsBuffer, prsCount, registers[FIFO_EMPTY]);
}

#ifndef DPS_DISABLESPI
int16_t Dps422::setInterruptSources(uint8_t intr_source, uint8_t polarity)
{
	// Intrrupt only supported by I2C or 3-Wire SPI
	if (!m_SpiI2c & !m_threeWire)
	{
		return DPS__FAIL_UNKNOWN;
	}

	return writeByteBitfield(intr_source, registers[INTR_SEL]) || writeByteBitfield(polarity, registers[INTR_POL]);
}
#endif

////////   private  /////////
void Dps422::init(void)
{
	// m_lastTempScal = 0.08716583251; // in case temperature reading disabled, the default raw temperature value correspond the reference temperature of 27 degress.
	standby();
	if (readcoeffs() < 0 || writeByteBitfield(0x01, registers[MUST_SET]) < 0)
	{
		m_initFail = 1U;
		return;
	}
	configTemp(DPS__MEASUREMENT_RATE_4, DPS__OVERSAMPLING_RATE_8);
	configPressure(DPS__MEASUREMENT_RATE_4, DPS__OVERSAMPLING_RATE_8);
	// get one temperature measurement for pressure compensation
	float trash;
	measureTempOnce(trash);
	standby();
	correctTemp();
}

int16_t Dps422::readcoeffs(void)
{
	uint8_t buffer_temp[3];
	uint8_t buffer_prs[20];
	readBlock(coeffBlocks[COEF_TEMP], buffer_temp);
	readBlock(coeffBlocks[COEF_PRS], buffer_prs);

	// refer to datasheet
	// 1. read T_Vbe, T_dVbe and T_gain
	int32_t t_gain = buffer_temp[0];													 // 8 bits
	int32_t t_dVbe = (uint32_t)buffer_temp[1] >> 1;										 // 7 bits
	int32_t t_Vbe = ((uint32_t)buffer_temp[1] & 0x01) | ((uint32_t)buffer_temp[2] << 1); // 9 bits

	getTwosComplement(&t_gain, 8);
	getTwosComplement(&t_dVbe, 7);
	getTwosComplement(&t_Vbe, 9);

	// 2. Vbe, dVbe and Aadc
	float Vbe = t_Vbe * 1.05031e-4 + 0.463232422;
	float dVbe = t_dVbe * 1.25885e-5 + 0.04027621;
	float Aadc = t_gain * 8.4375e-5 + 0.675;
	// 3. Vbe_cal and dVbe_cal
	float Vbe_cal = Vbe / Aadc;
	float dVbe_cal = dVbe / Aadc;
	// 4. T_calib
	float T_calib = DPS422_A_0 * dVbe_cal - 273.15;
	// 5. Vbe_cal(T_ref): Vbe value at reference temperature
	float Vbe_cal_tref = Vbe_cal - (T_calib - DPS422_T_REF) * DPS422_T_C_VBE;
	// 6. alculate PTAT correction coefficient
	float k_ptat = (DPS422_V_BE_TARGET - Vbe_cal_tref) * DPS422_K_PTAT_CORNER + DPS422_K_PTAT_CURVATURE;
	// 7. calculate A' and B'
	a_prime = DPS422_A_0 * (Vbe_cal + DPS422_ALPHA * dVbe_cal) * (1 + k_ptat);
	b_prime = -273.15 * (1 + k_ptat) - k_ptat * T_calib;

	// c00, c01, c02, c10 : 20 bits
	// c11, c12: 17 bits
	// c20: 15 bits; c21: 14 bits; c30 12 bits
	m_c00 = ((uint32_t)buffer_prs[0] << 12) | ((uint32_t)buffer_prs[1] << 4) | (((uint32_t)buffer_prs[2] & 0xF0) >> 4);
	m_c10 = ((uint32_t)(buffer_prs[2] & 0x0F) << 16) | ((uint32_t)buffer_prs[3] << 8) | (uint32_t)buffer_prs[4];
	m_c01 = ((uint32_t)buffer_prs[5] << 12) | ((uint32_t)buffer_prs[6] << 4) | (((uint32_t)buffer_prs[7] & 0xF0) >> 4);
	m_c02 = ((uint32_t)(buffer_prs[7] & 0x0F) << 16) | ((uint32_t)buffer_prs[8] << 8) | (uint32_t)buffer_prs[9];
	m_c20 = ((uint32_t)(buffer_prs[10] & 0x7F) << 8) | (uint32_t)buffer_prs[11];
	m_c30 = ((uint32_t)(buffer_prs[12] & 0x0F) << 8) | (uint32_t)buffer_prs[13];
	m_c11 = ((uint32_t)buffer_prs[14] << 9) | ((uint32_t)buffer_prs[15] << 1) | (((uint32_t)buffer_prs[16] & 0x80) >> 7);
	m_c12 = (((uint32_t)buffer_prs[16] & 0x7F) << 10) | ((uint32_t)buffer_prs[17] << 2) | (((uint32_t)buffer_prs[18] & 0xC0) >> 6);
	m_c21 = (((uint32_t)buffer_prs[18] & 0x3F) << 8) | ((uint32_t)buffer_prs[19]);

	getTwosComplement(&m_c00, 20);
	getTwosComplement(&m_c01, 20);
	getTwosComplement(&m_c02, 20);
	getTwosComplement(&m_c10, 20);
	getTwosComplement(&m_c11, 17);
	getTwosComplement(&m_c12, 17);
	getTwosComplement(&m_c20, 15);
	getTwosComplement(&m_c21, 14);
	getTwosComplement(&m_c30, 12);

	return DPS__SUCCEEDED;
}

int16_t Dps422::flushFIFO()
{
	return writeByteBitfield(1U, registers[FIFO_FL]);
}

float Dps422::calcTemp(int32_t raw)
{
	m_lastTempScal = (float)raw / 1048576;
	float u = m_lastTempScal / (1 + DPS422_ALPHA * m_lastTempScal);
	return (a_prime * u + b_prime);
}

float Dps422::calcPressure(int32_t raw_prs)
{
	float prs = raw_prs;
	prs /= scaling_facts[m_prsOsr];

	float temp = (8.5 * m_lastTempScal) / (1 + 8.8 * m_lastTempScal);

	prs = m_c00 + m_c10 * prs + m_c01 * temp + m_c20 * prs * prs + m_c02 * temp * temp + m_c30 * prs * prs * prs +
		  m_c11 * temp * prs + m_c12 * prs * temp * temp + m_c21 * prs * prs * temp;
	return prs;
}