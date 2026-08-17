#ifndef LIST_HPP
#define LIST_HPP

#include "Iterator.hpp"
#include "templategod.hpp"
#include "Map.hpp"
#include <list>

template <typename T>
class List : public std::list<T> {
private:
    typedef std::list<T>                         _lst;
    typedef typename _lst::iterator              _RawIter;
    typedef typename _lst::const_iterator        _RawCIter;
    typedef typename _lst::reverse_iterator      _RawRIter;
    typedef typename _lst::const_reverse_iterator _RawCRIter;

public:
    typedef Iterator<_RawIter>          iterator;
    typedef Iterator<_RawCIter>         const_iterator;
    typedef Iterator<_RawRIter>         reverse_iterator;
    typedef Iterator<_RawCRIter>        const_reverse_iterator;

    OK_CHECK(List)

    // --- Orthodox Canonical Form (Rule of Three - C++98) ---
    List() { _ok = false; }
    ~List() {}

    // Copy from other List
    List(const List& other) : _lst(other), _ok(other._ok) {}
    List& operator=(const List& other) { _lst::operator=(other), _ok = other._ok; return *this; }

    // Converting from std::list (copy only)
    List(const _lst& other) : _lst(other), _ok(true) {}
    List& operator=(const _lst& other) { _lst::operator=(other), _ok = true; return *this; }

    // --- List from container + function ---
    // Usage: List<Val> l(container, fn)  where fn(element) returns something with operator bool
    template <typename CONTAINER, typename FN>
    List(const CONTAINER& container, FN fn) {
        typedef typename fn_return_type<FN>::type result_type;
        _ok = true;
        if (container.size() == 0) { _ok = false; return; }
        for (size_t i = 0; i < container.size(); ++i) {
            result_type content = fn(container[i]);
            if (content) {
                add(content);
            }
        }
    }

    // --- Iterators (wrapping raw → Iterator) ---
    iterator begin()               { return iterator(_lst::begin()); }
    iterator end()                 { return iterator(_lst::end()).notok(); }
    const_iterator begin() const   { return const_iterator(_lst::begin()); }
    const_iterator end() const     { return const_iterator(_lst::end()).notok(); }
    reverse_iterator rbegin()      { return reverse_iterator(_lst::rbegin()); }
    reverse_iterator rend()        { return reverse_iterator(_lst::rend()).notok(); }
    const_reverse_iterator rbegin() const { return const_reverse_iterator(_lst::rbegin()); }
    const_reverse_iterator rend() const   { return const_reverse_iterator(_lst::rend()).notok(); }

    // --- add: push a value onto the list ---
    void add(const T& value) {
        _lst::push_back(value);
    }

    // --- add: push a value that has operator bool (e.g. Val, Pair) ---
    template <typename U>
    void add(const U& value) {
        if (value)
            _lst::push_back(value);
    }

    // --- operator(): chainable add ---
    List& operator()(const T& value) {
        add(value);
        return *this;
    }

    // --- map: transform each element via fn, produce new List ---
    // Usage: List<NewType> result = lst.map(myFunction);
    template <typename FN>
    List<typename fn_return_type<FN>::type> map(FN fn) const {
        List<typename fn_return_type<FN>::type> result;
        for (const_iterator it = this->begin(); it != this->end(); ++it) {
            typename fn_return_type<FN>::type content = fn(*it);
            if (content) {
                result.add(content);
            }
        }
        return result.ok();
    }

    template <typename FN>
    Map<typename fn_return_type<FN>::type::first_type, typename fn_return_type<FN>::type::second_type>
    toMap(FN fn) const {
        Map<typename fn_return_type<FN>::type::first_type, typename fn_return_type<FN>::type::second_type> result;
        for (const_iterator it = this->begin(); it != this->end(); ++it) {
            typename fn_return_type<FN>::type content = fn(*it);
            if (content) {
                result.add(content.first, content.second);
            }
        }
        return result.ok();
    }

    template <typename FN>
    List &forEach(FN fn) {
        for (iterator it = this->begin(); it != this->end(); ++it) {
            fn(*it);
        }
        return *this;
    }

};

#endif // LIST_HPP
