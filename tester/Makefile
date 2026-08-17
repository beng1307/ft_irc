NAME = testrunner
CXX = c++
CXXFLAGS = -Wall -Wextra -Werror -std=c++98

SRCS = testrunner.cpp
OBJS = $(SRCS:.cpp=.o)

all: $(NAME)

$(NAME): $(OBJS)
	$(CXX) $(CXXFLAGS) $(OBJS) -o $(NAME)

clean:
	rm -f $(OBJS)

fclean: clean
	rm -f $(NAME)
	rm -rf logs

re: fclean all

# Run testrunner with default scenarios or arguments passed to make run (e.g. make run 03)
run: $(NAME)
	-@./run_scenarios $(filter-out $@,$(MAKECMDGOALS))

# Run testrunner in verbose mode (e.g. make runv 35)
runv: $(NAME)
	@VERBOSE=1 ./run_scenarios $(filter-out $@,$(MAKECMDGOALS))

# Allow passing scenario arguments to 'make run' without make complaining about missing targets
%:
	@:

.PHONY: all clean fclean re run runv
