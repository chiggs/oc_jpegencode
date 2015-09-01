
PWD := $(shell pwd)
PROJECT := oc_jpegencode
TOP_LEVEL_ENTITY := jpeg_top
ASSIGNMENT_FILES := $(PROJECT).qpf $(PROJECT).qsf

VERILOG_SOURCES = $(PWD)/../code/y_huff.v \
                  $(PWD)/../code/y_quantizer.v \
                  $(PWD)/../code/y_dct.v \
                  $(PWD)/../code/cb_huff.v \
                  $(PWD)/../code/cb_quantizer.v \
                  $(PWD)/../code/cb_dct.v \
                  $(PWD)/../code/cr_huff.v \
                  $(PWD)/../code/cr_quantizer.v \
                  $(PWD)/../code/cr_dct.v \
                  $(PWD)/../code/yd_q_h.v \
                  $(PWD)/../code/cbd_q_h.v \
                  $(PWD)/../code/crd_q_h.v \
                  $(PWD)/../code/rgb2ycbcr.v \
                  $(PWD)/../code/sync_fifo_ff.v \
                  $(PWD)/../code/sync_fifo_32.v \
                  $(PWD)/../code/pre_fifo.v \
                  $(PWD)/../code/ff_checker.v \
                  $(PWD)/../code/fifo_out.v \
                  $(PWD)/../code/jpeg_top.v


FAMILY = "Cyclone V"



all: $(PROJECT).sta.rpt 

clean:
	rm -rf $(ASSIGNMENT_FILES) *.rpt *.summary *.chg smart.log *.htm *.eqn *.pin *.sof *.pof db incremental_db


MAP_ARGS = --read_settings_files=on $(addprefix --source=,$(VERILOG_SOURCES))
FIT_ARGS = --read_settings_files=on
STA_ARGS =

$(PROJECT).map.rpt: $(SOURCE_FILES) $(ASSIGNMENT_FILES)
	quartus_map $(MAP_ARGS) $(PROJECT)

$(PROJECT).fit.rpt: $(PROJECT).map.rpt
	quartus_fit $(FIT_ARGS) $(PROJECT)

$(PROJECT).sta.rpt: $(PROJECT).fit.rpt
	quartus_sta $(STA_ARGS) $(PROJECT)

$(ASSIGNMENT_FILES):
	quartus_sh --prepare -f $(FAMILY) -t $(TOP_LEVEL_ENTITY) $(PROJECT)

