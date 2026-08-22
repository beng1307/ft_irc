#include "../Int.hpp"
#include "../Wire.hpp"
#include "../print.hpp"
#include <cassert>

void testInt() {
    print("--- Running Int Tests ---");

    // 1. Constructors and OK checks
    Int i1;
    assert(!i1); // Default constructor sets _ok to false

    Int i2(42);
    assert(i2);
    assert(i2.val == 42);
    assert(i2 == 42);

    Int i3(i2);
    assert(i3);
    assert(i3 == 42);

    Int i4 = i2;
    assert(i4);
    assert(i4 == 42);

    // ok checks: ok(), notok(), setok()
    Int i_ok;
    assert(!i_ok);
    i_ok.ok();
    assert(i_ok);
    i_ok.notok();
    assert(!i_ok);
    i_ok.setok(true);
    assert(i_ok);
    i_ok.setok(false);
    assert(!i_ok);

    Int i_copy_ok(10);
    i_copy_ok.notok();
    Int i_target;
    i_target.setok(i_copy_ok);
    assert(!i_target);

    // copy() method
    Int i_orig(100);
    Int i_copied = i_orig.copy();
    assert(i_copied == 100);
    assert(i_copied);

    Int i_orig_notok(100);
    i_orig_notok.notok();
    Int i_copied_ok = i_orig_notok.copy();
    assert(i_copied_ok == 100);
    assert(i_copied_ok); // copy() forces ok()

    // 2. isZero()
    Int i_zero(0);
    Int i_nonzero(5);
    assert(i_zero.isZero() == true);
    assert(i_nonzero.isZero() == false);

    // 3. toStr()
    Int i_str_val(12345);
    Wire w1 = i_str_val.toStr();
    assert(w1 == "12345");
    assert(w1);

    Int i_invalid;
    Wire w_inv = i_invalid.toStr();
    assert(!w_inv);

    // 4. logError & logEmpty
    Int i_err;
    i_err.logError("Expected test log message for invalid Int");
    i_err.logEmpty("Expected test log message for Int empty check");

    // 5. Arithmetic operators (Int with Int)
    Int a(20);
    Int b(5);

    assert((a + b) == 25);
    assert((a - b) == 15);
    assert((a * b) == 100);
    assert((a / b) == 4);
    assert((a % b) == 0);

    // Division by zero
    Int zero(0);
    assert(!(a / zero)); // Division by zero sets _ok to false
    assert(!(a % zero));

    // OK propagation in arithmetic
    Int bad;
    assert(!(a + bad));
    assert(!(bad + b));
    assert(!(a - bad));
    assert(!(a * bad));
    assert(!(a / bad));
    assert(!(a % bad));

    // Raw int arithmetic
    assert((a + 10) == 30);
    assert((10 + a) == 30);
    assert((a - 5) == 15);
    assert((25 - a) == 5);
    assert((a * 2) == 40);
    assert((2 * a) == 40);
    assert((a / 2) == 10);
    assert((100 / a) == 5);

    // Compound assignment
    Int c(10);
    c += Int(5);
    assert(c == 15);
    c -= Int(3);
    assert(c == 12);
    c *= Int(2);
    assert(c == 24);
    c /= Int(4);
    assert(c == 6);

    // Increment / Decrement
    Int inc(5);
    assert(++inc == 6);
    assert(inc++ == 6);
    assert(inc == 7);
    assert(--inc == 6);
    assert(inc-- == 6);
    assert(inc == 5);

    // 6. Comparison operators
    Int x(10);
    Int y(20);
    Int x2(10);

    assert(x == x2);
    assert(x != y);
    assert(x < y);
    assert(y > x);
    assert(x <= x2);
    assert(x <= y);
    assert(y >= x);

    // Comparison with raw int
    assert(x == 10);
    assert(10 == x);
    assert(x != 20);
    assert(20 != x);
    assert(x < 20);
    assert(5 < x);
    assert(y > 10);
    assert(30 > y);
    assert(x <= 10);
    assert(10 <= x);
    assert(y >= 20);
    assert(20 >= y);

    // Comparison with invalid Int returns false
    assert((x == bad) == false);
    assert((x < bad) == false);
    assert((bad < x) == false);

    // 7. Conversions to other numeric types (e.g. size_t, unsigned int, long)
    Int num(42);
    size_t s1 = static_cast<size_t>(num);
    size_t s2 = num;
    unsigned int u = num;
    long l = num;
    unsigned long ul = num;
    assert(s1 == 42);
    assert(s2 == 42);
    assert(u == 42);
    assert(l == 42);
    assert(ul == 42);

    print("--- All Int Tests Passed Successfully ---");
}

void testFloat() {
    print("--- Running Float Tests ---");

    // 1. Constructors and OK checks
    Float f1;
    assert(!f1);

    Float f2(3.14f);
    assert(f2);
    assert(f2.val == 3.14f);
    assert(f2 == 3.14f);

    Float f3(f2);
    assert(f3);
    assert(f3 == 3.14f);

    Float f4 = f2;
    assert(f4);
    assert(f4 == 3.14f);

    // ok checks
    Float f_ok;
    assert(!f_ok);
    f_ok.ok();
    assert(f_ok);
    f_ok.notok();
    assert(!f_ok);
    f_ok.setok(true);
    assert(f_ok);

    // copy() method
    Float f_orig(2.718f);
    Float f_copied = f_orig.copy();
    assert(f_copied == 2.718f);
    assert(f_copied);

    // 2. isZero()
    Float f_zero(0.0f);
    Float f_nonzero(1.5f);
    assert(f_zero.isZero() == true);
    assert(f_nonzero.isZero() == false);

    // 3. toStr()
    Float f_str_val(123.45f);
    Wire w1 = f_str_val.toStr();
    assert(w1 == "123.45");
    assert(w1);

    Float f_invalid;
    Wire w_inv = f_invalid.toStr();
    assert(!w_inv);

    // 4. logError & logEmpty
    Float f_err;
    f_err.logError("Expected test log message for invalid Float");
    f_err.logEmpty("Expected test log message for Float empty check");

    // 5. Arithmetic operators
    Float a(10.5f);
    Float b(2.5f);

    assert((a + b) == 13.0f);
    assert((a - b) == 8.0f);
    assert((a * b) == 26.25f);
    assert((a / b) == 4.2f);

    // Division by zero
    Float zero(0.0f);
    assert(!(a / zero));

    // OK propagation
    Float bad;
    assert(!(a + bad));
    assert(!(bad + b));

    // Raw float arithmetic
    assert((a + 1.5f) == 12.0f);
    assert((1.5f + a) == 12.0f);
    assert((a - 0.5f) == 10.0f);
    assert((a * 2.0f) == 21.0f);
    assert((a / 2.0f) == 5.25f);

    // Compound assignment
    Float c(5.0f);
    c += Float(2.5f);
    assert(c == 7.5f);
    c -= Float(1.5f);
    assert(c == 6.0f);
    c *= Float(2.0f);
    assert(c == 12.0f);
    c /= Float(3.0f);
    assert(c == 4.0f);

    // Increment / Decrement
    Float inc(1.0f);
    assert(++inc == 2.0f);
    assert(inc++ == 2.0f);
    assert(inc == 3.0f);
    assert(--inc == 2.0f);
    assert(inc-- == 2.0f);
    assert(inc == 1.0f);

    // 6. Comparison operators
    Float x(1.0f);
    Float y(2.0f);

    assert(x != y);
    assert(x < y);
    assert(y > x);

    print("--- All Float Tests Passed Successfully ---");
}

int main() {
    testInt();
    testFloat();
    return 0;
}
