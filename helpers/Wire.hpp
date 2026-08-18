#ifndef WIRE_HPP
#define WIRE_HPP

#include <string>
#include <sstream>
#include <cctype>
#include <algorithm>
#include "abo.hpp"
#include "templategod.hpp"
#include "Int.hpp"
#include "Vector.hpp"
using std::string;



class Wire : public string {
public:
    // Orthodox Canonical Form
    Wire() : string(), _ok(true) {}
    Wire(const Wire& str) : string(str), _ok(str._ok) {}
    Wire& operator=(const Wire& other) {
        if (this != &other) {
            string::operator=(other);
            _ok = other._ok;
        }
        return *this;
    }
    ~Wire() {}

    // Additional constructors
    Wire(const string& str) : string(str), _ok(true) {}
    Wire(const char* str) : string(str ? str : ""), _ok(str != NULL) {}
    Wire(char c) : string(1, c), _ok(true) {}
    Wire(std::istream& ifs) : string(), _ok(false) { fromStream(ifs); }
    
#define MAKE_WIRE_TYPENAME(N) typename T##N
#define MAKE_WIRE_ARGUMENT(N) T##N const &t##N

#define MAKE_WIRE_CONSTRUCTOR(N) \
    template <FE(MAKE_WIRE_TYPENAME, MAKE_##N(INCREMENT, 0))> \
    Wire(FE(MAKE_WIRE_ARGUMENT, MAKE_##N(INCREMENT, 0))) : _ok(true) { \
        std::ostringstream ss; \
        std::ostream& os = ss; \
        abo(os, FE(PRINT_VAR, MAKE_##N(INCREMENT, 0))); \
        this->assign(ss.str()); \
    }

    FEX(MAKE_WIRE_CONSTRUCTOR, MAKE_30(INCREMENT, 0))

#undef MAKE_WIRE_TYPENAME
#undef MAKE_WIRE_ARGUMENT
#undef MAKE_WIRE_CONSTRUCTOR
    
    // replaceAll method
    Wire& replaceAll(const string& from, const string& to) {
        if (from.empty()) return *this;
        size_t start_pos = 0;
        while ((start_pos = this->find(from, start_pos)) != string::npos) {
            this->replace(start_pos, from.length(), to);
            start_pos += to.length();
        }
        return *this;
    }

    Wire reverse() const {
        string rev;
        for (int i = static_cast<int>(this->length()) - 1; i >= 0; --i) {
            rev += (*this)[i];
        }
        return Wire(rev);
    }

    Wire toUpper() const {
        Wire result(*this);
        for (size_t i = 0; i < result.length(); ++i) {
            result[i] = static_cast<char>(std::toupper(static_cast<unsigned char>(result[i])));
        }
        return result;
    }

    Wire toLower() const {
        Wire result(*this);
        for (size_t i = 0; i < result.length(); ++i) {
            result[i] = static_cast<char>(std::tolower(static_cast<unsigned char>(result[i])));
        }
        return result;
    }

    Wire& print() {
        ::print(*this);
        return *this;
    }

    Wire& fromStream(std::istream& ifs) {
        std::ostringstream ss;
        ss << ifs.rdbuf();
        this->assign(ss.str());
        _ok = !ifs.fail();
        return *this;
    }

    Wire strBefore(string delimiter) const {
        size_t pos = this->find(delimiter);
        if (pos == string::npos) return Wire();
        return Wire(this->substr(0, pos));
    }

    Wire strUntil(char delimiter) const {
        size_t pos = this->find(delimiter);
        if (pos == string::npos) return Wire();
        return Wire(this->substr(0, pos));
    }

    Wire strAfter(string delimiter) const {
        size_t pos = this->find(delimiter);
        if (pos == string::npos) return Wire();
        return Wire(this->substr(pos + delimiter.length(), string::npos));
    }

    Float toFloat() const {
        std::istringstream iss(*this);
        float f = 0.0f;
        iss >> f;
        if (iss.fail()) return Float();
        return Float(f);
    }

    Int toInt() const {
        std::istringstream iss(*this);
        int i = 0;
        iss >> i;
        if (iss.fail()) return Int();
        return Int(i);
    }

    Wire substr(size_t pos, size_t len = string::npos) const {
        if (pos >= this->length()) return Wire();
        return Wire(string::substr(pos, len));
    }

    Wire placeholder(const Wire& fallback) const {
        if (this->empty()) return fallback;
        return *this;
    }

    bool contains(string delimiter) const {
        return this->find(delimiter) != string::npos;
    }

    bool containsOneOf(const Vector<Wire>& options) const {
        for (size_t i = 0; i < options.size(); ++i) {
            if (contains(options[i])) return true;
        }
        return false;
    }

    bool containsOneOf(const string& chars) const {
        for (size_t i = 0; i < chars.length(); ++i) {
            if (this->find(chars[i]) != string::npos) return true;
        }
        return false;
    }

    bool hasOnly(const string& allowed) const {
        return !this->empty() && this->find_first_not_of(allowed) == string::npos;
    }

    template <typename FN>
    bool hasOnly(FN fn, const string& allowed = "") const {
        if (this->empty()) return false;
        for (size_t i = 0; i < this->length(); ++i) {
            unsigned char c = static_cast<unsigned char>((*this)[i]);
            if (!fn(static_cast<char>(c)) && (allowed.empty() || allowed.find(static_cast<char>(c)) == string::npos))
                return false;
        }
        return true;
    }

    static bool isAlpha(char c) { return std::isalpha(static_cast<unsigned char>(c)) != 0; }
    static bool isDigit(char c) { return std::isdigit(static_cast<unsigned char>(c)) != 0; }
    static bool isAlphaNum(char c) { return std::isalnum(static_cast<unsigned char>(c)) != 0; }

    bool hasOnlyAlpha(const string& extra = "") const { return hasOnly(isAlpha, extra); }
    bool hasOnlyDigits(const string& extra = "") const { return hasOnly(isDigit, extra); }
    bool hasOnlyAlphaNum(const string& extra = "") const { return hasOnly(isAlphaNum, extra); }

    Vector<Wire> splitBy(char delimiter, VectorTag = VectorTag()) const { return splitByImpl<Vector<Wire> >(delimiter); }
    Vector<Wire> splitChars(VectorTag = VectorTag()) const { return splitCharsImpl<Vector<Wire> >(); }

    bool is_empty() const { return this->empty(); }
    OK_CHECK(Wire);

private:
    template <typename Container>
    Container splitByImpl(char delimiter) const {
        Container result;
        std::istringstream iss(*this);
        string token;
        while (std::getline(iss, token, delimiter)) {
            result.add(Wire(token));
        }
        return result.ok();
    }

    template <typename Container>
    Container splitCharsImpl() const {
        Container result;
        for (size_t i = 0; i < this->length(); ++i) {
            result.add(Wire((*this)[i]));
        }
        return result.ok();
    }
};

inline bool isAlpha(char c) { return Wire::isAlpha(c); }
inline bool isDigit(char c) { return Wire::isDigit(c); }
inline bool isAlphaNum(char c) { return Wire::isAlphaNum(c); }

inline bool is_empty(const Wire& wire) {
    return wire.empty();
}

inline Wire Int::toStr() const {
    if (!_ok) return Wire().notok();
    return Wire(val);
}

inline Wire Float::toStr() const {
    if (!_ok) return Wire().notok();
    return Wire(val);
}

#endif
