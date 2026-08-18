#ifndef MAP_HPP
#define MAP_HPP

#include "Iterator.hpp"
#include "templategod.hpp"
#include <map>
#include "Pair.hpp"

template <typename Key, typename T>
class Map : public std::map<Key, T> {
private:
    typedef std::map<Key, T>                   _map;
    typedef typename _map::iterator            _RawIter;
    typedef typename _map::const_iterator      _RawCIter;
    typedef typename _map::reverse_iterator    _RawRIter;
    typedef typename _map::const_reverse_iterator _RawCRIter;

public:
    typedef Iterator<_RawIter>          iterator;
    typedef Iterator<_RawCIter>         const_iterator;
    typedef Iterator<_RawRIter>         reverse_iterator;
    typedef Iterator<_RawCRIter>        const_reverse_iterator;

    OK_CHECK(Map)

    // --- Orthodox Canonical Form (Rule of Three - C++98) ---
    Map() : _ok(false) {}
    ~Map() {}

    // Copy from other Map
    Map(const Map& other) : _map(other), _ok(other._ok) {}
    Map& operator=(const Map& other) { _map::operator=(other), _ok = other._ok; return *this; }

    // Converting from std::map (copy only)
    Map(const _map& other) : _map(other), _ok(true) {}
    Map& operator=(const _map& other) { _map::operator=(other), _ok = true; return *this; }

    // --- Map from container + function ---
    // Usage: Map<Key,Val> m(container, fn)  where fn(element) returns something with .first/.second and operator bool
    template <typename CONTAINER, typename FN>
    Map(const CONTAINER& container, FN fn) : _ok(true) {
        typedef typename fn_return_type<FN>::type result_type;
        if (container.size() == 0) { _ok = false; return; }
        for (size_t i = 0; i < container.size(); ++i) {
            result_type content = fn(container[i]);
            if (content) {
                add(content.first, content.second);
            }
        }
    }

    // --- Iterators (wrapping raw → Iterator) ---
    iterator begin()               { return iterator(_map::begin()); }
    iterator end()                 { return iterator(_map::end()).notok(); }
    const_iterator begin() const   { return const_iterator(_map::begin()); }
    const_iterator end() const     { return const_iterator(_map::end()).notok(); }
    reverse_iterator rbegin()      { return reverse_iterator(_map::rbegin()); }
    reverse_iterator rend()        { return reverse_iterator(_map::rend().notok()); }
    const_reverse_iterator rbegin() const { return const_reverse_iterator(_map::rbegin()); }
    const_reverse_iterator rend() const   { return const_reverse_iterator(_map::rend()).notok(); }

    // --- FIND: returns Iterator with _ok flag ---
    iterator find(const Key& key) {
        _RawIter it = _map::find(key);
        if (it != _map::end())
            return iterator(it);
        return this->end();     // equal to end(), _ok defaults to false
    }

    // --- LOWER_BOUND: first element >= key, or not-found ---
    iterator lower_bound(const Key& key) {
        _RawIter it = _map::lower_bound(key);
        if (it != _map::end())
            return iterator(it);
        return this->end();     // equal to end(), _ok defaults to false
    }

    iterator upper_bound(const Key& key) {
        _RawIter it = _map::upper_bound(key);
        if (it != _map::end())
            return iterator(it);
        return this->end();     // equal to end(), _ok defaults to false
    }
    // matching element or smaller element than key or not found
    iterator smaller_bound(const Key& key) {
        _RawIter it = _map::lower_bound(key);
        if (it != _map::end() && it->first == key)
            return iterator(it);
        if (it == _map::begin())
            return this->end();
        --it;
        return iterator(it);
    }
    const_iterator smaller_bound(const Key& key) const {
        _RawCIter it = _map::lower_bound(key);
        if (it != _map::end() && it->first == key)
            return const_iterator(it);
        if (it == _map::begin())
            return this->end();
        --it;
        return const_iterator(it);
    }
    const_iterator find(const Key& key) const {
        _RawCIter it = _map::find(key);
        if (it != _map::end())
            return const_iterator(it);
        return this->end();
    }

    void erase(iterator pos) {
        this->_map::erase(pos.base());
    }
    void erase(iterator first, iterator last) {
        this->_map::erase(first.base(), last.base());
    }
    size_t erase(const Key& key) {
        return this->_map::erase(key);
    }

    void add(const Key& key, const T& value) {
        _map::insert(std::make_pair(key, value));
    }
    template <typename A, typename B>
    void add(Pair<A, B> p) {
        if(p)
            _map::insert(std::make_pair(p.first, p.second));
    }
    template <typename Key_arg, typename T_arg>
    Map & operator()( const Key_arg& key, const T_arg& value) {
        add(key, value);
        return *this;
    }

    // --- Map set operations (return copies) ---
    Map add(const Map& b) const {
        Map result(*this);
        for (_RawCIter it = b._map::begin(); it != b._map::end(); ++it) {
            result._map::insert(*it);
        }
        return result.ok();
    }

    Map merge(const Map& b) const {
        return add(b);
    }

    Map subtract(const Map& b) const {
        Map result(*this);
        for (_RawCIter it = b._map::begin(); it != b._map::end(); ++it) {
            result.erase(it->first);
        }
        return result.ok();
    }

    Map subtract(const Key& key) const {
        Map result(*this);
        result.erase(key);
        return result.ok();
    }

    Map difference(const Map& b) const {
        Map result;
        for (_RawCIter it = this->_map::begin(); it != this->_map::end(); ++it) {
            if (b.find(it->first) == b.end())
                result.add(it->first, it->second);
        }
        for (_RawCIter it = b._map::begin(); it != b._map::end(); ++it) {
            if (this->find(it->first) == this->end())
                result.add(it->first, it->second);
        }
        return result.ok();
    }

    Map operator+(const Map& b) const {
        return add(b);
    }

    Map operator+(const std::pair<Key, T>& p) const {
        Map result(*this);
        result.add(p.first, p.second);
        return result.ok();
    }

    template <typename A, typename B>
    Map operator+(const Pair<A, B>& p) const {
        Map result(*this);
        result.add(p);
        return result.ok();
    }

    Map operator-(const Map& b) const {
        return subtract(b);
    }

    Map operator-(const Key& key) const {
        return subtract(key);
    }
};

#endif // MAP_HPP