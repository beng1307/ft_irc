#include "../Style.hpp"
#include <cassert>
#include <iostream>

int main() {
    Style s1("Hello ", 42, "Worlds");
    assert(s1 == "Hello 42Worlds");

    Style s2 = Style("Error").red().padx(3);
    assert(s2 == "\033[31m   Error   \033[0;0m");

    Style s3 = Style("Ok").green().padx(2);
    assert(s3 == "\033[0;32m  Ok  \033[0;0m");

    Style s4 = Style("Test").padl(2).padr(1);
    assert(s4 == "  Test ");

    Style s5 = Style("Top").padt(2);
    assert(s5 == "\n\nTop");

    Style s6 = Style("Bottom").padb(2);
    assert(s6 == "Bottom\n\n");

    Style s7 = Style("Y").pady(1);
    assert(s7 == "\nY\n");

    Style s8 = Style("Styled").red().pady(1).padl(1);
    assert(s8 == "\033[31m \nStyled\n\033[0;0m");

    Style s9 = $("Hello ", 42).red().padx(5);
    assert(s9 == "\033[31m     Hello 42     \033[0;0m");

    Style s10 = $().green().padx(5)("HELLO", 42, "WORLD");
    assert(s10 == "\033[0;32m     HELLO42WORLD     \033[0;0m");

    Style s11 = $().padx(5)("HELLO")("WORLD");
    assert(s11 == "     HELLO          WORLD     ");

    Style s12 = $("BOBB").center(12);
    assert(s12 == "    BOBB    ");

    Style s13 = $("BOB").center(12);
    assert(s13 == "    BOB     ");

    Style s14 = $("TEST").width(10);
    assert(s14 == "TEST      ");

    Style s15 = $("TEST").widthl(10);
    assert(s15 == "      TEST");

    Style s16 = $().textc(0, 0, 0).bgc(255, 0, 0)("HELLO WORLD");
    assert(s16 == "\033[38;2;0;0;0m\033[48;2;255;0;0mHELLO WORLD\033[0;0m");

    $().textc(0, 0, 0).bgc(255, 0, 0)("HELLO WORLD FROM PRINT METHOD").print();

    std::cout << "Style tests passed!" << std::endl;
    return 0;
}
