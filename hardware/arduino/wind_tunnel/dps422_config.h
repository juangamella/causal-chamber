
#ifndef DPS422_CONFIG_H_
#define DPS422_CONFIG_H_

// consts for temperature calculation
#define DPS422_T_REF 27
#define DPS422_V_BE_TARGET 0.687027
#define DPS422_ALPHA 9.45
#define DPS422_T_C_VBE -1.735e-3
#define DPS422_K_PTAT_CORNER -0.8
#define DPS422_K_PTAT_CURVATURE 0.039
#define DPS422_A_0 5030

#define DPS422_NUM_OF_REGMASKS 20

enum Interrupt_source_420_e
{
    DPS422_NO_INTR = 0,
    DPS422_PRS_INTR = 1,
    DPS422_TEMP_INTR = 2,
    DPS422_BOTH_INTR = 3,
    DPS422_FIFO_WM_INTR = 4,
    DPS422_FIFO_FULL_INTR = 8,
};

namespace dps422
{
enum Registers_e
{
    // flags
    CONT_FLAG = 0, // continuous mode flag
    INIT_DONE,     // set when initialisation procedure is complete
    // interrupt config
    INTR_SEL, // interrupt select
    INTR_POL, // interrupt active polarity
    // fifo config
    WM,              // watermark level
    FIFO_FL,         // FIFO flush
    FIFO_EMPTY,      // FIFO empty
    FIFO_FULL,       // if FIFO is full or reaches watermark level
    FIFO_FULL_CONF,  // Configures FIFO behaviour when full
    FIFO_FILL_LEVEL, //contains the number of pressure and/or temperature measurements currently stored in FIFO
    // misc
    PROD_ID,
    REV_ID,
    SPI_MODE, // 4- or 3-wire SPI
    SOFT_RESET,
    MUST_SET, // bit 7 of TEMP_CFG, according to datasheet should always be set
};

const RegMask_t registers[DPS422_NUM_OF_REGMASKS] = {
    // flags
    {0x08, 0x40, 6}, // CONT_FLAG
    {0x08, 0x80, 7}, // INIT_DONE
    // interrupt config
    {0x09, 0xF0, 4}, // INTR_SEL
    {0x09, 0x80, 3}, // INTR_POL
    // /fifo config
    {0x0B, 0x1F, 0}, // WM
    {0x0D, 0x80, 7}, // FIFO_FL
    {0x0C, 0x01, 0}, // FIFO_EMPTY
    {0x0C, 0x02, 1}, // FIFO_FULL
    {0x09, 0x04, 2}, // FIFO_FULL_CONF
    {0x0C, 0xFC, 2}, // FIFO_FILL_LEVEL
    // misc
    {0x1D, 0x0F, 0}, // PROD_ID
    {0x1D, 0xF0, 0}, // REV_ID
    {0x09, 0x01, 0}, // SPI_MODE
    {0x0D, 0x0F, 0}, // SOFT_RESET
    {0x07, 0x80, 7}, // MUST_SET
};

enum RegisterBlocks_e
{
    COEF_TEMP, // compensation coefficients
    COEF_PRS,
};

const RegBlock_t coeffBlocks[4] = {
    {0x20, 3},
    {0x26, 20},
};

} // namespace dps422

#endif /* DPS422_CONSTS_H_ */
