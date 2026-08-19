NAME = testrunner
CONCURRENCY_NAME = concurrency_tester
CXX = c++
CXXFLAGS = -Wall -Wextra -Werror -std=c++98 -pthread

SRCS = testrunner.cpp
OBJS = $(SRCS:.cpp=.o)

CONCURRENCY_SRCS = concurrency_tester.cpp
CONCURRENCY_OBJS = $(CONCURRENCY_SRCS:.cpp=.o)

all: $(NAME) $(CONCURRENCY_NAME)

$(NAME): $(OBJS)
	$(CXX) $(CXXFLAGS) $(OBJS) -o $(NAME)

$(CONCURRENCY_NAME): $(CONCURRENCY_OBJS)
	$(CXX) $(CXXFLAGS) $(CONCURRENCY_OBJS) -o $(CONCURRENCY_NAME)

clean:
	rm -f $(OBJS) $(CONCURRENCY_OBJS)

fclean: clean
	rm -f $(NAME) $(CONCURRENCY_NAME)
	rm -rf logs

re: fclean all

# Run testrunner with default scenarios or arguments passed to make run (e.g. make run 03)
run: $(NAME)
	-@./run_scenarios $(filter-out $@,$(MAKECMDGOALS))

# Run testrunner in verbose mode (e.g. make runv 35)
runv: $(NAME)
	@VERBOSE=1 ./run_scenarios $(filter-out $@,$(MAKECMDGOALS))

lifecycle:
	@./test_server_lifecycle.sh

concurrency: $(CONCURRENCY_NAME)
	@./$(CONCURRENCY_NAME)

memory:
	@python3 ./test_memory_dos.py

# Allow passing scenario arguments to 'make run' without make complaining about missing targets
%:
	@:

.PHONY: all clean fclean re run runv lifecycle concurrency memory
