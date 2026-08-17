#include "../Wire.hpp"
#include "../print.hpp"
#include <cassert>
#include <sstream>

int main() {
    print("--- Running Wire Tests ---");

    // 1. Basic constructors
    Wire w1;
    assert(w1 == "");

    Wire w2("hello");
    assert(w2 == "hello");

    std::string std_str = "world";
    Wire w3(std_str);
    assert(w3 == "world");

    Wire w4('A');
    assert(w4 == "A");

    Wire w5(w2);
    assert(w5 == "hello");

    Wire w6 = w3;
    assert(w6 == "world");

    // 2. Multi-argument variadic stream constructors
    Wire w_multi1("Count: ", 5, " true: ", true);
    assert(w_multi1 == "Count: 5 true: 1");

    Wire w_multi2("A", 'B', 123, 45.6);
    assert(w_multi2 == "AB12345.6");

    // 3. String manipulation methods
    Wire w_rep("hello world world");
    w_rep.replaceAll("world", "nanoirc");
    assert(w_rep == "hello nanoirc nanoirc");

    Wire w_rev("abcde");
    assert(w_rev.reverse() == "edcba");

    Wire w_delim("user@host:port");
    assert(w_delim.strBefore("@") == "user");
    assert(w_delim.strUntil('@') == "user");
    assert(w_delim.strAfter("host:") == "port");

    Wire w_sub("0123456789");
    assert(w_sub.substr(2, 4) == "2345");

    // 4. Checking containment
    Wire w_check("hello world");
    assert(w_check.contains("world") == true);
    assert(w_check.contains("missing") == false);
    assert(w_check.containsOneOf("xyzo") == true);
    assert(w_check.containsOneOf("xyz") == false);

    Vector<Wire> options;
    options.push_back("foo");
    options.push_back("world");
    assert(w_check.containsOneOf(options) == true);

    // 5. Conversions & OK status checks
    Wire w_num("12345");
    Int i_val = w_num.toInt();
    assert(i_val == 12345);
    assert(i_val); // OK status is true
    assert(i_val.toStr() == "12345");
    assert(i_val.copy() == 12345);
    assert(i_val.copy());

    Wire w_invalid("abc");
    Int i_invalid = w_invalid.toInt();
    assert(!i_invalid); // OK status is false / notok
    assert(!i_invalid.toStr());

    Wire w_float("123.45");
    Float f_val = w_float.toFloat();
    assert(f_val == 123.45f);
    assert(f_val); // OK status is true
    assert(f_val.toStr() == "123.45");
    assert(f_val.copy() == 123.45f);
    assert(f_val.copy());

    Wire w_invalid_float("xyz");
    Float f_invalid = w_invalid_float.toFloat();
    assert(!f_invalid); // OK status is false / notok
    assert(!f_invalid.toStr());

    // 6. Stream loading & OK state
    std::istringstream iss("stream_text");
    Wire w_stream;
    w_stream.fromStream(iss);
    assert(w_stream == "stream_text");
    assert(w_stream); // OK status is true

    Wire w_ok_test("valid Wire");
    assert(w_ok_test);
    w_ok_test.notok();
    assert(!w_ok_test); // notok status verified
    w_ok_test.ok();
    assert(w_ok_test); // ok status restored

    Wire w_err;
    w_err.notok();
    w_err.logError("Simulated error for notok test");
    assert(!w_err); // logError checks notok

    Pair<int, int> p1(10, 20);
    assert(p1);
    p1.notok();
    p1.logError("Pair error log test");
    p1.logEmpty("Pair logEmpty no-op test");
    assert(!p1);

    // 7. Print method
    w_multi1.print();

    print("--- All Wire Tests Passed Successfully ---");
    return 0;
}
