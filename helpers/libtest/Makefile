CXX = c++
CXXFLAGS = -Wall -Wextra -Werror -std=c++98

all: wire int style

wire: WireTest.cpp
	$(CXX) $(CXXFLAGS) WireTest.cpp -o WireTest
	./WireTest

int: IntTest.cpp
	$(CXX) $(CXXFLAGS) IntTest.cpp -o IntTest
	./IntTest

style: StyleTest.cpp
	$(CXX) $(CXXFLAGS) StyleTest.cpp -o StyleTest
	./StyleTest

clean:
	rm -f WireTest WireTest.o IntTest IntTest.o StyleTest StyleTest.o

.PHONY: all wire int style clean

