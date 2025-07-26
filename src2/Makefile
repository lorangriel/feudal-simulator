INC := $(shell sdl2-config --cflags 2>/dev/null)

CFLAGS = 	-Wall -g -O2 $(INC) -MD

LIBS := $(shell sdl2-config --libs 2>/dev/null)

LDFLAGS =	-rdynamic

TARGET =	sdl_run

SRC = 		Main.cpp \

OBJ = 		$(patsubst %.cpp, %.o, $(SRC))

%.o: %.cpp
	$(CXX) $(CFLAGS) -c $< -o $@

PROGS = 	$(TARGET)

all: 		$(PROGS)

$(TARGET): 	$(OBJ)
		g++ -o $@ $^ $(LIBS) $(LDFLAGS)
