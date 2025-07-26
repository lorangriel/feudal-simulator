INC =

CFLAGS = 	-Wall -g -O2 $(INC) -MD

LIBS =

LDFLAGS =	-rdynamic

TARGET =	sdl_run

SRC = 		Main.cpp \

OBJ = 		$(patsubst %.cpp, %.o, $(SRC))

PROGS = 	$(TARGET)

all: 		$(PROGS)

$(TARGET): 	$(OBJ)
		g++ -o $@ $^ $(LIBS) $(LDFLAGS)
