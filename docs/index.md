# OpenCores JPEG Encoder

Originally hosted on [OpenCores](http://opencores.org/project,jpegencode).

Code and text by David Lundgren.


## Introduction

This document describes the JPEG Encoder IP Core provided.  The core is written in Verilog and is designed to be portable to any target device.  This core does not perform subsampling - the resulting JPEG image will have 4:4:4 subsampling.

## Inputs

The top level module is `jpeg_top`, in the file [jpeg_top.v](https://github.com/chiggs/oc_jpegencode/blob/master/code/jpeg_top.v).

The inputs to the core are kept to a minimum.  The first 3 inputs are the clock, enable, and reset lines.  One global clock is used throughout the design, and all of the registers are synchronized to the rising edge of this clock.  The enable signal should be brought high when the data from the first pixel of the image is ready.  The enable signal needs to stay high while the data is being input to the core.  Each 8x8 block of data needs to be input to the core on 64 consecutive clock cycles.  After the 64 pixels of data from each block has been input, the enable signal needs to stay high for a minimum of 33 clock cycles.  There should not be any new data during this delay of 33 or more clock cycles.  Then the enable signal should be brought low for one clock cycle, then brought high again as the next 8x8 block of data is input to the core.  This pattern needs to continue for each of the 8x8 blocks of data.

The data bus is 24 bits wide.  The red, green, and blue pixel values are input on the bus.  Each pixel value is represented in 8 bits, corresponding to a value between 0-255.  The pixel values can be extracted directly from a .tif file for example.  The blue pixel value is in bits [23:16], green is in bits [15:8], and red is in bits [7:0] of the data bus.

The only other input is the end_of_file_signal.  This signal needs to go high on the first clock cycle of valid data bits of the final 8x8 block of the image.  This signal lets the core know it needs to output all of the bits from this last block.  The output bitstream is a 32-bit bus, and normally between blocks, any bits that don’t fill the whole 32-bit width output bus will not be output.  Instead, they will be added to the initial bits from the next 8x8 block of the image.  On the last 8x8 block, the core will output any extra bits so that there are not any missing bits from the image.

## Outputs

The JPEG bitstream is output on the signal JPEG_bitstream, a 32-bit bus.  The first 8 bits will be in positions [31:24], the next 8 bits are in [23:16], and so on.  The data in JPEG_bitstream is valid when the signal is data_ready is high.  data_ready will only be high for one clock cycle to indicate valid data.  On the final block of data, if the last bits do not fill the 32-bit bus, the signal eof_data_partial_ready will be high for one clock cycle when the extra bits are in the signal JPEG_bitstream.  The number of extra bits is indicated by the 5-bit signal `end_of_file_bitstream_count`.


## Operation of the JPEG Encoder core

### Color Space Transformation

The first operation of the JPEG Encoder core is converting the red, green, and blue pixel values to their corresponding Luminance and Chrominance (Y, Cb, and Cr) values.  This operation is performed in the `RGB2YCBCR` module.  The operation is based on the following formulas:

```
    Y = .299 * Red  +  .587 * Green  +  .114 * Blue
    Cb = -.1687 * Red  +  -.3313 * Green  + .5 * Blue + 128
    Cr = .5 * Red  +  -.4187 * Green  +  -.0813 * Blue + 128
```

These operations are performed with fixed point multiplications.  All of the constant values in the above 3x3 matrix are multiplied by 2^14 (16384).   The multiplications are performed on one clock cycle, then all of the products are added together on the next clock cycle.  This is done to achieve a fast clock frequency during synthesis.  Then the sums are divided by 2^14, which is implemented by discarding the 14 LSBs of the sum values, instead of actually performing a divide operation.  Rounding is performed by looking at the 13th LSB and adding 1 to the sum if the 13th LSB is 1.

### Discrete Cosine Transform

The next step after calculating the Y, Cb, and Cr values is performing the Discrete Cosine Transform (DCT).  This is commonly referred to as a 2D DCT.  The actual formula is the following:

```
    DY = T * Y * inv(T)
```

T is the DCT matrix.  Y is the matrix of Y values for the 8x8 image block.  DY is the resultant matrix after the 2D DCT.  The DCT needs to be performed separately on the Y, Cb, and Cr values for each block.  The DCT of the Y values is performed in the `y_dct` module.  The DCT of the Cb and Cr values occurs in the cb_dct and cr_dct modules.  I will only describe the `y_dct` module here, as the `cb_dct` and `cr_dct` modules are essentially the same.

Now you may have noticed that I have not centered the Y, Cb, and Cr values on 0 in the previous stage.  To do that, I would have subtracted 128 from the final Y value, and not added the 128 to the final Cb and Cr values.  To perform the DCT, the values of Y, Cb, and Cr need to be centered around 0 and in the range –128 to 127.  However, I perform a few tricks in the DCT module that allow me to keep the Y, Cb, and Cr values in the range from 0-255.  I do this because it makes the implementation of the DCT easier.  

The DCT matrix, or T as I call it, is multiplied by the constant value 16384 or 2^14.  The rows of the T matrix are orthonormal (the entries in each row add up to 0), except for the first row.  Because the rows 2-8 are orthonormal, it does not matter that I have not centered the Y values on 0.  I perform the multiplication of the T rows by the Y columns of data, and the extra 128 in each of the Y values is cancelled out by the orthonormal T rows.  The first row, however, is not orthonormal - it has a constant value of .3536, or 5793 after it is multiplied by 2^14.  Since I have not centered Y by 0, the extra 128 in each value will result in an extra 128*8*5793 = 5932032 in the final sum.  So to make up for the fact that I have not centered the Y values on 0, I subtract 5932032 from the result of the first row of T multiplied by each of the 8 columns of the Y matrix.  If you think about this, it means I have to perform a total of 8 subtractions for an 8x8 matrix of Y values.  If I had subtracted 128 from each Y value before the DCT module, I would have needed to perform a total of 64 subtractions.

After multiplying the T matrix by the Y matrix, the resulting matrix is multiplied by the inverse of the T matrix.  This operation is performed in the code with the goal of achieving the highest possible clock frequency for the design.  The result is the code may look overly confusing, but I tried many different schemes before settling on the one used in the code.  I would simulate the code, verify it worked, then synthesize to see what clock speed I could achieve, and I repeated this process many times until I got around 300 MHz as the best clock speed.  I targeted a Xilinx Virtex 5 FPGA to achieve this speed.

### Quantization

The next step is fairly straightforward.  The module `y_quantizer` comes next for the Y values.  The Cb and Cr values go through the `cb_quantizer` and `cr_quantizer` modules.  The 64 quantization values are stored in the parameters Q1_1 through Q8_8.  I used finals values of 1 for my core, but you could change these values to any quantization you want.  I simulated different quantization values during testing, and I settled on values of 1, corresponding to Q = 100, because this stressed my code the most and I was trying to break the core in my final testing.  The core did not break, it worked, but I left the quantization values as they were.

As in previous stages, I avoid performing actual division as this would be an unnecessary and burdensome calculation to perform.  I create other parameters QQ1_1 through QQ8_8, and each value is 4096 divided by Q1_1 through Q8_8.  For example, QQ1_1 = 4096 / Q1_1.  This division is performed when the code is compiled, so it doesn’t require division in the FPGA.

The input values are multiplied by their corresponding parameter values, QQ1_1 through QQ8_8.  Then, the bottom 12 bits are chopped off the product.  This gets rid of the 4096, or 2^12, that was used to create the parameters QQ1_1 through QQ8_8.  The final values are rounded based on the value in the 11th LSB.

### Huffman Encoding

The module `y_huff` performs the Huffman encoding of the quantized Y values coming out of the `y_quantizer` module.  The modules `cb_huff` and `cr_huff` perform the Huffman encoding for the Cb and Cr values.  The module `yd_q_h` combines the `y_dct`, `y_quantizer`, and `y_huff` modules.  The values from `y_quantizer` are transposed (rows swapped with columns) as they are input to the `y_huff` module.  This is done so that the inputs of each 8x8 block to the top module, `jpeg_top`, can be written in the traditional left to right order.  Peforming the DCT requires matrix multiplication, and the rows of the T matrix are multiplied by the columns of the Y matrix.  So the Y values would need to be entered in a column format, from top to bottom, to implement this.  Instead, the Y values can be entered in the traditional row format, from left to right, and then by transposing the values as they pass between the `y_quantizer` and `y_huff` modules, the proper organization of Y values is regained.

The Huffman table can be changed by changing the values in this module – the specific lines of code with the Huffman table are lines 1407-1930.  However, the core does not allow the Huffman table to be changed on the fly.  You will have to recompile the code to change the Huffman table.  You should create a full Huffman table, even if you have a small image file and do not expect to use all of the Huffman codes.  The calculations in this core may differ slightly from how you do your calculations, and if you use a Huffman table without all of the possible values defined, the core may need a Huffman code that is not stored in the RAM, and the result will be an incorrect bitstream output.

The DC component is calculated first, then the AC components are calculated in zigzag order.  The output from the `y_huff` module is a 32-bits signal containing the Huffman codes and amplitudes for the Y values.

### Creating the Output JPEG Bitstream

The outputs from the `y_huff`, `cb_huff`, and `cr_huff` modules are combined into the pre_fifo module, along with the RGB2YCBCR module.  The `pre_fifo` module organizes those modules into one module, but does not add any additional logic or functions.  The next module in the hierarchy is the `fifo_out` module.  This module takes the `pre_fifo` module and combines it with 3 `sync_fifo_32 modules`.

The `sync_fifo_32` modules are necessary to hold the outputs from the y_huff, cb_huff, and cr_huff modules.  The `sync_fifo_32` module is 16 registers deep.  The depth of the FIFO’s should be increased if the Quantization Table is small, which could cause the FIFO’s to overflow.  I did not have an overflow of any of the images I encoded, but if you have more than 512 (32*16) bits of data for one block from the Cb or Cr blocks, then the data will overflow the FIFO.  The Y block FIFO is read from more often than the Cb and Cr blocks, so it will not overflow.  The output JPEG bitstream combines the Y, Cb, and Cr Huffman codes together, and it starts with the Y Huffman codes, followed by the Cb Huffman codes, and finally the Cr Huffman codes for each 8x8 block of the image.  Then the Huffman codes from the next 8x8 block of the image are put into the bitstream.

After the fifo_out module comes the `ff_checker` module.  The `ff_checker` module looks for any ‘FF’s in the bitstream that occur on the byte boundaries.  When an ‘FF’ is found, a ‘00’ is put into the bitstream after the ‘FF’, and then the rest of the bitstream follows.  The ff_checker module uses a `sync_fifo` module to store data as it checks the bits for the ‘FF’s.

The top level module of the JPEG Encoder core is the `jpeg_out` module.  This module combines the `ff_checker` module and the `fifo_out` module. 

## Testbench

### Verilog TB

The testbench file, jpeg_top_TB.v, inputs the data from the image ‘ja.tif’ into the JPEG Encoder core.  I used a Matlab program to extract the red, green, and blue pixel values directly from the ‘ja.tif’ file and write it in the correct testbench format.  This testbench was used to simulate the core and to verify its correct operation.  The output from the core during simulation was the JPEG scan data bitstream, which was used to create the jpeg image file ‘ja.jpg’.  The output from the core was the scan data portion of the jpeg image file.  The header was copied from a separate jpeg image that also had dimensions of 96x96 pixels.  I used the Huffman tables and Quantizations tables from this separate jpeg image to create ja.jpg.  The Huffman and Quantization tables are also the ones I used in the code of this core, otherwise the resultant bitstream would not correspond to the JPEG header I used.  Also, the end of the jpeg image needs to have the end of scan marker, ‘FFD9’.

### Cocotb TB

A [Cocotb](http://cocotb.com) testbench has been created that uses the Python Imaging Library to take
any image file and drive it through the core, comparing the JPEG output similarity to the original image.  This code resides in the [tb](https://github.com/chiggs/oc_jpegencode/tree/master/tb) directory.



