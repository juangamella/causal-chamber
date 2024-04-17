/**
 * @brief 
 * 
 * Temperature measurements must be enabled for the DPS422 to compensate for temperature drift in the pressure measurement.
 * @file Dps422.h
 * @author Infineon Technologies
 * @date 2018-08-22
 */

#ifndef DPS422_H_INCLUDED
#define DPS422_H_INCLUDED
#include "DpsClass.h"
#include "util/dps422_config.h"

class Dps422 : public DpsClass
{
public:
  int16_t getContResults(float *tempBuffer, uint8_t &tempCount, float *prsBuffer, uint8_t &prsCount);

  /**
   * @brief Set the source of interrupt (FIFO full, measurement values ready)
   * 
   * @param intr_source Source of interrupt as defined by Interrupt_source_420_e
   * @param polarity 
   * @return int16_t 
   */
  int16_t setInterruptSources(uint8_t intr_source, uint8_t polarity = 1);

  /**
   * @brief measures both temperature and pressure values, when op mode is set to CMD_BOTH
   * 
   * @param prs reference to the pressure value
   * @param temp prs reference to the temperature value
   * @return status code
   */
  int16_t measureBothOnce(float &prs, float &temp); // might make sense to declare in base class for future sensors

  int16_t measureBothOnce(float &prs, float &temp, uint8_t prs_osr, uint8_t temp_osr);

protected:
  //compensation coefficients (for simplicity use 32 bits)
  float a_prime;
  float b_prime;
  int32_t m_c02;
  int32_t m_c12;

  /////// implement pure virtual functions ///////
  void init(void);
  int16_t readcoeffs(void);
  int16_t flushFIFO();
  float calcTemp(int32_t raw);
  float calcPressure(int32_t raw);
};

#endif