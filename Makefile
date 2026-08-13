COMPILE = c++ -g -Wall -Wextra -Werror -std=c++98 -fPIE
NAME = ft_irc
SRCS = main.cpp \
	   Channel/Channel.cpp \
	   Client/Client.cpp \
	   Server/Server.cpp \
	   Server/ServerSocket.cpp \
	   Server/ServerLoop.cpp \
	   Server/ServerCommands.cpp \
	   Server/ServerChannelOps.cpp \
	   Server/ServerMessaging.cpp \
	   Server/ServerHelper.cpp
OBJS_FOLDER = obj
OBJS = $(SRCS:%.cpp=$(OBJS_FOLDER)/%.o)
HEADERS = Server/Server.hpp Channel/Channel.hpp Client/Client.hpp 

$(NAME): $(OBJS)
	$(COMPILE) $(OBJS) -o $(NAME)	

$(OBJS_FOLDER)/%.o: %.cpp $(HEADERS)
	@mkdir -p $(dir $@)
	$(COMPILE) -c $< -o $@

all: $(NAME)

clean:
	@rm -rf $(OBJS_FOLDER)

fclean:	clean
	@rm -f $(NAME)

re: fclean all

run: all
	@./ft_irc 6667 1234

client: all
	irssi -c localhost -p 6667 -w 1234


.PHONY: all clean fclean re