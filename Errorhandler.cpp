#include "Errorhandler.hpp"

bool	Errorhandler::right_amount_of_args(const int &ac)
{
	if (ac == 3)
		return (true);
	else
		return (false);
}