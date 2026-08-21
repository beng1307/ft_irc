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

-include ../.env
-include .env

ENV_PORT := $(PORT)
ENV_PASSWORD := $(PASSWORD)
PORT := $(if $(ENV_PORT),$(ENV_PORT),6667)
PASSWORD := $(if $(ENV_PASSWORD),$(ENV_PASSWORD),1234)

# make run [port] [pass] OR make run [pass] OR make run = run all scenarios
run: $(NAME)
	@set -- $(filter-out $@,$(MAKECMDGOALS)); \
	if [ $$# -ge 2 ]; then \
		./run_scenarios --port "$$1" --password "$$2"; \
	elif [ $$# -eq 1 ]; then \
		./run_scenarios --port $(PORT) --password "$$1"; \
	else \
		./run_scenarios; \
	fi

# make case [testcase] OR make case [pass] [testcase] OR make case [port] [pass] [testcase]
case: $(NAME)
	@set -- $(filter-out $@,$(MAKECMDGOALS)); \
	if [ $$# -eq 1 ]; then \
		./run_scenarios "$$1"; \
	elif [ $$# -eq 2 ]; then \
		./run_scenarios --port $(PORT) --password "$$1" "$$2"; \
	elif [ $$# -ge 3 ]; then \
		./run_scenarios --port "$$1" --password "$$2" "$$3"; \
	else \
		echo "Usage: make case <testcase>  OR  make case <pass> <testcase>  OR  make case <port> <pass> <testcase>"; \
		exit 1; \
	fi

# make caseverbose [testcase] OR make caseverbose [pass] [testcase] OR make caseverbose [port] [pass] [testcase]
caseverbose: $(NAME)
	@set -- $(filter-out $@,$(MAKECMDGOALS)); \
	if [ $$# -eq 1 ]; then \
		VERBOSE=1 ./run_scenarios "$$1"; \
	elif [ $$# -eq 2 ]; then \
		VERBOSE=1 ./run_scenarios --port $(PORT) --password "$$1" "$$2"; \
	elif [ $$# -ge 3 ]; then \
		VERBOSE=1 ./run_scenarios --port "$$1" --password "$$2" "$$3"; \
	else \
		echo "Usage: make caseverbose <testcase>  OR  make caseverbose <pass> <testcase>  OR  make caseverbose <port> <pass> <testcase>"; \
		exit 1; \
	fi

# Alias for make caseverbose
runv: caseverbose

lifecycle:
	@./test_server_lifecycle.sh

concurrency: $(CONCURRENCY_NAME)
	@./ensure_server.sh ./$(CONCURRENCY_NAME) $(filter-out $@,$(MAKECMDGOALS))

memory:
	@python3 ./test_memory_dos.py

# make env [port] [password] = edits / saves .env (or removes .env if no args)
env:
	@set -- $(filter-out $@,$(MAKECMDGOALS)); \
	if [ $$# -ge 2 ]; then \
		echo "PORT=$$1" > .env; \
		echo "PASSWORD=$$2" >> .env; \
		echo "Saved to .env -> PORT=$$1, PASSWORD=$$2"; \
	elif [ $$# -eq 0 ]; then \
		rm -f .env; \
		echo "Removed .env (reset to defaults)"; \
	else \
		echo "Usage: make env <port> <password>  (or 'make env' to remove)"; \
	fi

help:
	@echo "Usage: make [target] [args...]"
	@echo ""
	@echo "  make                                - Compile testrunner and concurrency_tester"
	@echo "  make run                            - Run all scenarios"
	@echo "  make run <password>                 - Run all scenarios with custom password (port: .env or 6667)"
	@echo "  make run <port> <password>          - Run all scenarios with custom port and password"
	@echo "  make case <testcase>                - Run single test scenario"
	@echo "  make case <password> <testcase>     - Run single test scenario with custom password"
	@echo "  make case <port> <password> <case>  - Run single test scenario with custom port and password"
	@echo "  make caseverbose <testcase>         - Run single test scenario in verbose mode"
	@echo "  make caseverbose <pass> <testcase>  - Run single test scenario with custom password in verbose mode"
	@echo "  make caseverbose <p> <pass> <case>  - Run single test scenario with custom port & pass in verbose mode"
	@echo "  make runv <testcase>                - Alias for make caseverbose"
	@echo "  make concurrency                    - Run concurrency and thread-safety tests"
	@echo "  make lifecycle                      - Run server lifecycle and reboot tests"
	@echo "  make memory                         - Run memory / leak / stress tests"
	@echo ""
	@echo "  [.env file = persist custom port/password configuration]"
	@echo ""
	@echo "  make env <port> <password>          - Save default port and password to .env"
	@echo "  make env                            - Delete .env and reset to defaults"
	@echo "  make clean / fclean / re            - Clean object files, binaries, or rebuild"

# Allow passing scenario arguments to 'make run' without make complaining about missing targets
%:
	@:

.PHONY: all clean fclean re run runv case caseverbose lifecycle concurrency memory env help
