PROJECT   =    resnet50

CXX       :=   g++
CC        :=   gcc
OBJ       :=   main.o

# linking libraries of OpenCV
LDFLAGS   =   $(shell pkg-config --libs opencv)
# linking libraries of DNNDK
LDFLAGS   +=  -lhineon -ln2cube -ldputils

CUR_DIR =   $(shell pwd)
SRC     =   $(CUR_DIR)
BUILD   =   $(CUR_DIR)/tmp
MODEL   =   /root/samples/resnet50/model
VPATH   =   $(SRC)
ARCH= $(shell uname -m | sed -e s/arm.*/armv71/ \
	-e s/aarch64.*/aarch64/ )

CFLAGS    :=  -O2 -Wall -Wpointer-arith -std=c++11 -ffast-math
ifeq ($(ARCH),armv71)
	CFLAGS +=  -mcpu=cortex-a9 -mfloat-abi=hard -mfpu=neon
endif
ifeq ($(ARCH),aarch64)
	CFLAGS += -mcpu=cortex-a53
endif
WEIGHTS = $(MODEL)/dpu_resnet50_0.elf $(MODEL)/dpu_resnet50_2.elf

.PHONY: all clean

all: $(BUILD) $(PROJECT)

$(PROJECT) : $(OBJ)
	$(CXX) $(CFLAGS) $(addprefix $(BUILD)/, $^) $(WEIGHTS) -o $(BUILD)/$@ $(LDFLAGS)

%.o : %.cc
	$(CXX) -c $(CFLAGS) $< -o $(BUILD)/$@

clean:
	$(RM) -rf $(BUILD)
	$(RM) $(PROJECT)

$(BUILD) :
	-mkdir -p $@
