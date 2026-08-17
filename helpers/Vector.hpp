#ifndef VECTOR_HPP
#define VECTOR_HPP

#include "Iterator.hpp"
#include "templategod.hpp"
#include "Map.hpp"
#include "print.hpp"
#include <string>
#include <vector>


#ifndef REF_DEFINED
#define REF_DEFINED
template <typename U>
struct Ref {
    U* ptr;
    Ref(U& r) : ptr(&r) {}
    operator U&() { return *ptr; }
};
#endif

#ifndef FESTATE_DEFINED
#define FESTATE_DEFINED
namespace detail {
    template <typename RES, typename Item>
    struct fe_adder {
        static void add(RES* res, const Item& item) {
            if (res) res->add(item);
        }
    };

    template <typename Item>
    struct fe_adder<void, Item> {
        static void add(void*, const Item&) {}
    };
}

template <typename VEC, typename RES = void>
struct FEstate {
    size_t           index;
    bool             is_first;
    bool             is_last;
    const VEC&       array;
    bool             is_even;
    bool             is_odd;
    size_t           size;
    RES*             result;

    FEstate(size_t i, bool first, bool last, const VEC& arr, RES* res = NULL)
        : index(i), is_first(first), is_last(last), array(arr),
          is_even((i + 1) % 2 == 0), is_odd((i + 1) % 2 != 0),
          size(arr.size()), result(res) {}

    template <typename Item>
    void add(const Item& item) const {
        detail::fe_adder<RES, Item>::add(result, item);
    }

    typename VEC::value_type next(int offset = 1) const {
        size_t target = index + offset;
        if (target >= array.size()) return typename VEC::value_type();
        return array[target];
    }

    typename VEC::value_type prev(int offset = 1) const {
        if (index < (size_t)offset) return typename VEC::value_type();
        return array[index - offset];
    }
};
#endif

template <typename T>
class Vector : public std::vector<T> {
private:
    typedef std::vector<T>                         _vec;
    typedef typename _vec::iterator                _RawIter;
    typedef typename _vec::const_iterator          _RawCIter;
    typedef typename _vec::reverse_iterator        _RawRIter;
    typedef typename _vec::const_reverse_iterator  _RawCRIter;

public:
    typedef Iterator<_RawIter>          iterator;
    typedef Iterator<_RawCIter>         const_iterator;
    typedef Iterator<_RawRIter>         reverse_iterator;
    typedef Iterator<_RawCRIter>        const_reverse_iterator;

    OK_CHECK(Vector)

    Ref<Vector<T> > ref() { return Ref<Vector<T> >(*this); }

    // --- Orthodox Canonical Form (Rule of Three - C++98) ---
    Vector() { _ok = false; }
    Vector(const T& value) : _vec(1, value), _ok(true) {}
    ~Vector() {}

    // Copy from other Vector
    Vector(const Vector& other) : _vec(other), _ok(other._ok) {}
    Vector& operator=(const Vector& other) { _vec::operator=(other), _ok = other._ok; return *this; }

    // Converting from std::vector (copy only)
    Vector(const _vec& other) : _vec(other), _ok(true) {}
    Vector& operator=(const _vec& other) { _vec::operator=(other), _ok = true; return *this; }

    // --- Vector from container + function ---
    // Usage: Vector<Val> v(container, fn)  where fn(element) returns something with operator bool
    template <typename CONTAINER, typename FN>
    Vector(const CONTAINER& container, FN fn) {
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
    iterator begin()               { return iterator(_vec::begin()); }
    iterator end()                 { return iterator(_vec::end()).notok(); }
    const_iterator begin() const   { return const_iterator(_vec::begin()); }
    const_iterator end() const     { return const_iterator(_vec::end()).notok(); }
    reverse_iterator rbegin()      { return reverse_iterator(_vec::rbegin()); }
    reverse_iterator rend()        { return reverse_iterator(_vec::rend()).notok(); }
    const_reverse_iterator rbegin() const { return const_reverse_iterator(_vec::rbegin()); }
    const_reverse_iterator rend() const   { return const_reverse_iterator(_vec::rend()).notok(); }

    // --- insert: unwrap Iterator wrapper to raw iterator ---
    iterator insert(iterator pos, const T& value) {
        _RawIter raw = _vec::insert(pos.base(), value);
        return iterator(raw);
    }

    // --- insertAt: insert value at specific index ---
    Vector& insertAt(size_t index, const T& value) {
        _vec::insert(_vec::begin() + index, value);
        return *this;
    }

    // --- add: push a value onto the vector ---
    Vector& add(const T& value) {
        _vec::push_back(value);
        return *this;
    }

    // --- add: push a value that has operator bool (e.g. Val, Pair) ---
    template <typename U>
    Vector& add(const U& value) {
        if (value)
            _vec::push_back(value);
        return *this;
    }

    // --- operator(): chainable add ---
    Vector& operator()(const T& value) {
        return add(value);
    }
        // pop returns the last element and removes it
    T pop() {
        if(this->empty()) return T();
        T val = this->back();
        this->pop_back();
        return val;
    }
    // pop_first removes and returns the first element
    T pop_first() {
        if(this->empty()) return T();
        T val = this->front();
        _vec::erase(_vec::begin());
        return val;
    }

    // --- map: transform each element via fn (strict 1:1 mapping) ---
    // Usage: Vector<NewType> result = vec.map(myFunction);
    template <typename R, typename Arg>
    Vector<R> map(R (*fn)(Arg)) const {
        Vector<R> result;
        for (size_t i = 0; i < this->size(); ++i) {
            result.add(fn((*this)[i]));
        }
        return result.ok();
    }

    template <typename R, typename Arg, typename Index>
    Vector<R> map(R (*fn)(Arg, Index)) const {
        Vector<R> result;
        for (size_t i = 0; i < this->size(); ++i) {
            result.add(fn((*this)[i], i));
        }
        return result.ok();
    }

    // --- mapFilter: transform each element via fn and filter invalid values ---
    template <typename R, typename Arg>
    Vector<R> mapFilter(R (*fn)(Arg)) const {
        Vector<R> result;
        for (size_t i = 0; i < this->size(); ++i) {
            R content = fn((*this)[i]);
            if (is_valid_value(content)) {
                result.add(content);
            }
        }
        return result.ok();
    }

    template <typename R, typename Arg, typename Index>
    Vector<R> mapFilter(R (*fn)(Arg, Index)) const {
        Vector<R> result;
        for (size_t i = 0; i < this->size(); ++i) {
            R content = fn((*this)[i], i);
            if (is_valid_value(content)) {
                result.add(content);
            }
        }
        return result.ok();
    }

    // --- mapBy2: transform adjacent pairs via fn(T, T) -> R ---
    template <typename FN>
    Vector<typename fn_return_type<FN>::type> mapBy2(FN fn) const {
        typedef typename fn_return_type<FN>::type R;
        Vector<R> result;
        for (size_t i = 0; i < this->size(); i += 2) {
            T elem1 = (*this)[i];
            T elem2 = (i + 1 < this->size()) ? (*this)[i + 1] : T();
            R content = fn(elem1, elem2);
            if (is_valid_value(content)) {
                result.add(content);
            }
        }
        return result.ok();
    }

    // --- mapX: like map but passes FEstate instead of just index ---
    template <typename FN>
    Vector<typename fn_return_type<FN>::type> mapX(FN fn) const {
        typedef typename fn_return_type<FN>::type R;
        Vector<R> result;
        for (size_t i = 0; i < this->size(); ++i) {
            FEstate<Vector<T>, Vector<R> > st(i, i == 0, i == this->size() - 1, *this, &result);
            R content = fn((*this)[i], st);
            if (is_valid_value(content)) {
                result.add(content);
            }
        }
        return result.ok();
    }

    // --- mapX with extra arg: fn(element, FEstate, A1) ---
    template <typename FN, typename A1>
    Vector<typename fn_return_type<FN>::type> mapX(FN fn, A1 a1) const {
        typedef typename fn_return_type<FN>::type R;
        Vector<R> result;
        for (size_t i = 0; i < this->size(); ++i) {
            FEstate<Vector<T>, Vector<R> > st(i, i == 0, i == this->size() - 1, *this, &result);
            R content = fn((*this)[i], st, a1);
            if (is_valid_value(content)) {
                result.add(content);
            }
        }
        return result.ok();
    }

    // --- mapEntire: fn receives the entire Vector and returns a new Vector ---
    template <typename FN>
    typename fn_return_type<FN>::type mapEntire(FN fn) const {
        return fn(*this);
    }

    // --- mapEntire: fn receives the entire Vector and returns a new Vector ---
    template <typename FN, typename A1>
    typename fn_return_type<FN>::type mapEntire(FN fn, A1 a1) const {
        return fn(*this, a1);
    }

    // --- container (template): repackage values into TargetCont<T> ---
    template <template <typename> class TargetCont>
    TargetCont<T> container() const {
        TargetCont<T> result;
        for (size_t i = 0; i < this->size(); ++i) {
            result.add((*this)[i]);
        }
        return result.ok();
    }

    // --- container (instance): repackage values into explicit target container argument ---
    // Usage: vec.container(Deque<int>()) or vec.container(iArr())
    template <typename TargetContainer>
    TargetContainer container(TargetContainer) const {
        TargetContainer result;
        for (size_t i = 0; i < this->size(); ++i) {
            result.add((*this)[i]);
        }
        return result.ok();
    }

    // --- filter: remove elements where fn returns true, keep where false ---
    // Usage: Vector<Val> filtered = vec.filter(myFunction);
    template <typename FN>
    Vector filter(FN fn) const {
        Vector result;
        for (size_t i = 0; i < this->size(); ++i) {
            if (!fn((*this)[i]))
                result.add((*this)[i]);
        }
        return result.ok();
    }

        // --- reduce (1-arg): fold over the vector without initial acc ---
    template <typename FN>
    typename fn_return_type<FN>::type reduce(FN fn) const {
        typedef typename fn_return_type<FN>::type Acc;
        if (this->empty()) return Acc();
        Vector copy(*this);
        Acc acc = copy.pop_first();
        while (!copy.empty()) {
            acc = fn(acc, copy.pop_first());
            if(detail::break_if_falsy<detail::is_boolable<Acc>::value, Acc>::check(acc)) break;
        }
        return acc;
    }

        // --- reduce: fold over the vector. fn(Acc, T) -> Acc ---
    template <typename Acc, typename FN>
    Acc reduce(FN fn, Acc acc) const {
        Vector copy(*this); // make a copy to avoid modifying the original vector during iteration
        while (!copy.empty()) {
            acc = fn(acc, copy.pop_first());
            if(detail::break_if_falsy<detail::is_boolable<Acc>::value, Acc>::check(acc)) break;
        }
        return acc;
    }

    // --- reduce with extra arg passed by reference: fn(Acc, T, A1&) -> Acc ---
    template <typename Acc, typename FN, typename A1>
    Acc reduce(FN fn, Acc acc, A1 a1) const {
        Vector copy(*this);
        while (!copy.empty()) {
            acc = fn(acc, copy.pop_first(), a1);
            if(detail::break_if_falsy<detail::is_boolable<Acc>::value, Acc>::check(acc)) break;
        }
        return acc;
    }

    // --- reduce with two extra args: fn(Acc, T, A1, A2) -> Acc ---
    template <typename Acc, typename FN, typename A1, typename A2>
    Acc reduce(FN fn, Acc acc, A1 a1, A2 a2) const {
        Vector copy(*this);
        while (!copy.empty()) {
            acc = fn(acc, copy.pop_first(), a1, a2);
            if(detail::break_if_falsy<detail::is_boolable<Acc>::value, Acc>::check(acc)) break;
        }
        return acc;
    }

    // --- reduceX (1-arg): fold over vector passing FEstate without initial acc ---
    template <typename FN>
    typename fn_return_type<FN>::type reduceX(FN fn) const {
        typedef typename fn_return_type<FN>::type Acc;
        return reduceX(fn, Acc().ok());
    }

    // --- reduceX: like reduce but passes an FEstate (is_first/is_last/index) to fn ---
    // Usage: acc = vec.reduceX(fn, acc);  fn(Acc, T, FEstate<Vector<T> >) -> Acc
    template <typename Acc, typename FN>
    Acc reduceX(FN fn, Acc acc) const {
        Vector copy(*this);
        size_t i = 0;
        while (!copy.empty()) {
            bool is_last = copy.size() == 1;
            FEstate<Vector<T> > st(i, i == 0, is_last, *this);
            acc = fn(acc, copy.pop_first(), st);
            if(detail::break_if_falsy<detail::is_boolable<Acc>::value, Acc>::check(acc)) break;
            i++;
        }
        return acc;
    }

    // --- reduceX with one extra arg: fn(Acc, T, FEstate, A1) -> Acc ---
    template <typename Acc, typename FN, typename A1>
    Acc reduceX(FN fn, Acc acc, A1 a1) const {
        Vector copy(*this);
        size_t i = 0;
        while (!copy.empty()) {
            bool is_last = copy.size() == 1;
            FEstate<Vector<T> > st(i, i == 0, is_last, *this);
            acc = fn(acc, copy.pop_first(), st, a1);
            if(detail::break_if_falsy<detail::is_boolable<Acc>::value, Acc>::check(acc)) break;
            i++;
        }
        return acc;
    }


    // --- reduceX with one extra arg: fn(Acc, T, FEstate, A1) -> Acc ---
    template <typename Acc, typename FN, typename A1, typename A2>
    Acc reduceX(FN fn, Acc acc, A1 a1, A2 a2) const {
        Vector copy(*this);
        size_t i = 0;
        while (!copy.empty()) {
            bool is_last = copy.size() == 1;
            FEstate<Vector<T> > st(i, i == 0, is_last, *this);
            acc = fn(acc, copy.pop_first(), st, a1, a2);
            if(detail::break_if_falsy<detail::is_boolable<Acc>::value, Acc>::check(acc)) break;
            i++;
        }
        return acc;
    }

            // --- reduceBy2: fold over pairs. fn(Acc, T, T) -> Acc ---
    template <typename Acc, typename FN>
    Acc reduceBy2(FN fn, Acc acc) const {
        Vector copy(*this); // make a copy to avoid modifying the original vector during iteration
        while (copy.size() >= 2) {
            acc = fn(acc, copy.pop_first(), copy.pop_first());
            if(detail::break_if_falsy<detail::is_boolable<Acc>::value, Acc>::check(acc)) break;
        }
        if (!copy.empty())
            acc = fn(acc, copy.pop_first(), T());
        return acc;
    }

                // --- reduceBy2: fold over pairs. fn(Acc, T, T) -> Acc ---
    template <typename Acc, typename FN>
    Acc reduceBy2X(FN fn, Acc acc) const {
        Vector copy(*this); // make a copy to avoid modifying the original vector during iteration
        size_t i = 0;
        while (copy.size() >= 2) {
            FEstate<Vector<T> > st(i, i == 0, false, *this);
            acc = fn(acc, copy.pop_first(), copy.pop_first(), st);
            if(detail::break_if_falsy<detail::is_boolable<Acc>::value, Acc>::check(acc)) break;
            i++;
        }
        FEstate<Vector<T> > st(i, i == 0, true, *this);
        if (!copy.empty())
            acc = fn(acc, copy.pop_first(), T(), st);
        return acc;
    }

    // --- reduceTable: for a Vector of Vectors, accumulate acc across columns of each row ---
    // Usage: acc = table.reduceTable(acc_fn, acc);  acc_fn(Acc, ColumnValue) -> Acc
    template <typename Acc, typename FN>
    Acc reduceTable(FN acc_fn, Acc acc) const {
        for (size_t r = 0; r < this->size(); ++r) {
            acc = (*this)[r].reduce(acc_fn, acc);
            if(detail::break_if_falsy<detail::is_boolable<Acc>::value, Acc>::check(acc)) break;
        }
        return acc;
    }

    // --- reduceTableX: fold over a table (Vector of Vectors) passing column and row FEstates ---
    // Usage: acc = table.reduceTableX(acc_fn, acc);
    // acc_fn(acc, val, column_state, row_state) -> acc
    template <typename Acc, typename FN>
    Acc reduceTableX(FN acc_fn, Acc acc) const {
        for (size_t r = 0; r < this->size(); ++r) {
            FEstate<Vector<T> > row_st(r, r == 0, r == this->size() - 1, *this);
            acc = (*this)[r].reduceX(acc_fn, acc, row_st);
            if(detail::break_if_falsy<detail::is_boolable<Acc>::value, Acc>::check(acc)) break;
        }
        return acc;
    }

    // --- reduceTableX with extra arg: acc_fn(acc, val, column_state, row_state, extra_arg) -> acc ---
    template <typename Acc, typename FN, typename A1>
    Acc reduceTableX(FN acc_fn, Acc acc, A1 a1) const {
        for (size_t r = 0; r < this->size(); ++r) {
            FEstate<Vector<T> > row_st(r, r == 0, r == this->size() - 1, *this);
            acc = (*this)[r].reduceX(acc_fn, acc, row_st, a1);
            if(detail::break_if_falsy<detail::is_boolable<Acc>::value, Acc>::check(acc)) break;
        }
        return acc;
    }

    // --- reduceTableX (1-arg V2): fold over a table without passing initial acc or extra args ---
    template <typename FN>
    typename fn_return_type<FN>::type reduceTableX(FN acc_fn) const {
        typedef typename fn_return_type<FN>::type Acc;
        Acc acc = Acc().ok();
        for (size_t r = 0; r < this->size(); ++r) {
            T row = (*this)[r].reverse();
            for (size_t c = 0; c < row.size(); ++c) {
                if (row[c].bigger)
                    acc.add(row[c].bigger);
            }
        }
        for (size_t r = 0; r < this->size(); ++r) {
            FEstate<Vector<T> > row_st(r, r == 0, r == this->size() - 1, *this);
            acc = (*this)[r].reduceX(acc_fn, acc, row_st);
            if(detail::break_if_falsy<detail::is_boolable<Acc>::value, Acc>::check(acc)) break;
        }
        return acc;
    }

    // --- reduceTable (1-arg V2): fold acc_fn(acc, val) over a table without passing initial acc ---
    template <typename FN>
    typename fn_return_type<FN>::type reduceTable(FN acc_fn) const {
        typedef typename fn_return_type<FN>::type Acc;
        Acc acc = Acc().ok();
        for (size_t r = 0; r < this->size(); ++r) {
            T row = (*this)[r].reverse();
            for (size_t c = 0; c < row.size(); ++c) {
                if (row[c].bigger)
                    acc.add(row[c].bigger);
            }
        }
        for (size_t r = 0; r < this->size(); ++r) {
            acc = (*this)[r].reduce(acc_fn, acc);
            if(detail::break_if_falsy<detail::is_boolable<Acc>::value, Acc>::check(acc)) break;
        }
        return acc;
    }

    // --- keep: keep elements where fn returns true, remove where false ---
    // Usage: Vector<Val> kept = vec.keep(myFunction);
    template <typename FN>
    Vector keep(FN fn) const {
        Vector result;
        for (size_t i = 0; i < this->size(); ++i) {
            if (fn((*this)[i]))
                result.add((*this)[i]);
        }
        return result.ok();
    }

    // --- count: count elements where fn returns truthy ---
    // Usage: size_t n = vec.count(myPredicate);
    template <typename FN>
    size_t count(FN fn) const {
        size_t cnt = 0;
        for (size_t i = 0; i < this->size(); ++i) {
            if (fn((*this)[i]))
                ++cnt;
        }
        return cnt;
    }

    template <typename FN, typename A1>
    size_t count(FN fn, A1 a1) const {
        size_t cnt = 0;
        for (size_t i = 0; i < this->size(); ++i) {
            if (fn((*this)[i], a1))
                ++cnt;
        }
        return cnt;
    }

    // --- includes: return true if the element exists in the vector (using ==) ---
    bool includes(const T& value) const {
        for (size_t i = 0; i < this->size(); ++i) {
            if ((*this)[i] == value)
                return true;
        }
        return false;
    }

    // --- findIf: return first element where fn returns true, or T() if not found ---
    // Usage: T found = vec.findIf(myPredicate);
    template <typename FN>
    T findIf(FN fn) const {
        for (size_t i = 0; i < this->size(); ++i) {
            if (fn((*this)[i]))
                return (*this)[i];
        }
        return T();
    }
    // --- findIf with optional fn2 or extra arg: applies fn1 first ---
    template <typename FN, typename A1>
    T findIf(FN fn, A1 a1) const {
        for (size_t i = 0; i < this->size(); ++i) {
            if (detail::exec_find_if_2_dispatch<
                    detail::find_if_helper<FN, A1, T>::can_call_2,
                    detail::find_if_helper<FN, A1, T>::is_fn2
                >::exec(fn, a1, (*this)[i]))
                return (*this)[i];
        }
        return T();
    }
    // --- findIf with 2 functions and target value: fn2(fn1(entry), value_to_find) ---
    template <typename FN1, typename FN2, typename A1>
    T findIf(FN1 fn1, FN2 fn2, A1 a1) const {
        for (size_t i = 0; i < this->size(); ++i) {
            if (fn2(fn1((*this)[i]), a1))
                return (*this)[i];
        }
        return T();
    }

    // --- findIndex: return index of first element where fn returns true, or -1 if not found ---
    template <typename FN>
    int findIndex(FN fn) const {
        for (size_t i = 0; i < this->size(); ++i) {
            if (fn((*this)[i]))
                return static_cast<int>(i);
        }
        return -1;
    }
    template <typename FN, typename A1>
    int findIndex(FN fn, A1 a1) const {
        for (size_t i = 0; i < this->size(); ++i) {
            if (detail::exec_find_if_2_dispatch<
                    detail::find_if_helper<FN, A1, T>::can_call_2,
                    detail::find_if_helper<FN, A1, T>::is_fn2
                >::exec(fn, a1, (*this)[i]))
                return static_cast<int>(i);
        }
        return -1;
    }
    template <typename FN1, typename FN2, typename A1>
    int findIndex(FN1 fn1, FN2 fn2, A1 a1) const {
        for (size_t i = 0; i < this->size(); ++i) {
            if (fn2(fn1((*this)[i]), a1))
                return static_cast<int>(i);
        }
        return -1;
    }

    // --- findIfNot: return first element where fn returns false (!fn(el)), or T() if not found ---
    template <typename FN>
    T findIfNot(FN fn) const {
        for (size_t i = 0; i < this->size(); ++i) {
            if (!fn((*this)[i]))
                return (*this)[i];
        }
        return T();
    }
    template <typename FN, typename A1>
    T findIfNot(FN fn, A1 a1) const {
        for (size_t i = 0; i < this->size(); ++i) {
            if (!detail::exec_find_if_2_dispatch<
                    detail::find_if_helper<FN, A1, T>::can_call_2,
                    detail::find_if_helper<FN, A1, T>::is_fn2
                >::exec(fn, a1, (*this)[i]))
                return (*this)[i];
        }
        return T();
    }
    template <typename FN1, typename FN2, typename A1>
    T findIfNot(FN1 fn1, FN2 fn2, A1 a1) const {
        for (size_t i = 0; i < this->size(); ++i) {
            if (!fn2(fn1((*this)[i]), a1))
                return (*this)[i];
        }
        return T();
    }

    // --- findIndexNot: return index of first element where fn returns false, or -1 if not found ---
    template <typename FN>
    int findIndexNot(FN fn) const {
        for (size_t i = 0; i < this->size(); ++i) {
            if (!fn((*this)[i]))
                return static_cast<int>(i);
        }
        return -1;
    }
    template <typename FN, typename A1>
    int findIndexNot(FN fn, A1 a1) const {
        for (size_t i = 0; i < this->size(); ++i) {
            if (!detail::exec_find_if_2_dispatch<
                    detail::find_if_helper<FN, A1, T>::can_call_2,
                    detail::find_if_helper<FN, A1, T>::is_fn2
                >::exec(fn, a1, (*this)[i]))
                return static_cast<int>(i);
        }
        return -1;
    }
    template <typename FN1, typename FN2, typename A1>
    int findIndexNot(FN1 fn1, FN2 fn2, A1 a1) const {
        for (size_t i = 0; i < this->size(); ++i) {
            if (!fn2(fn1((*this)[i]), a1))
                return static_cast<int>(i);
        }
        return -1;
    }

    template <typename FN>
    Map<typename fn_return_type<FN>::type::first_type, typename fn_return_type<FN>::type::second_type>
    toMap(FN fn) const {
        return Map<typename fn_return_type<FN>::type::first_type, typename fn_return_type<FN>::type::second_type>(*this, fn);
    }

    template <typename FN>
    Vector &forEachforEach(FN fn) {
        for (size_t i = 0; i < this->size(); ++i) {
            (*this)[i].forEach(fn, (*this)[i]);
        }
        return *this;
    }
    template <typename FN>
    Vector &forEach(FN fn) {
        for (size_t i = 0; i < this->size(); ++i) {
            fn((*this)[i]);
        }
        return *this;
    }
    template <typename FN, typename A1>
    Vector &forEach(FN fn, A1 a1) {
        for (size_t i = 0; i < this->size(); ++i) {
            fn((*this)[i], a1);
        }
        return *this;
    }
    template <typename FN, typename A1, typename A2>
    Vector &forEach(FN fn, A1 a1, A2 a2) {
        for (size_t i = 0; i < this->size(); ++i) {
            fn((*this)[i], a1, a2);
        }
        return *this;
    }
    template <typename FN, typename A1, typename A2, typename A3>
    Vector &forEach(FN fn, A1 a1, A2 a2, A3 a3) {
        for (size_t i = 0; i < this->size(); ++i) {
            fn((*this)[i], a1, a2, a3);
        }
        return *this;
    }
    template <typename FN>
    Vector &forEach_i(FN fn) {
        for (size_t i = 0; i < this->size(); ++i) {
            fn((*this)[i], i);
        }
        return *this;
    }
    template <typename FN, typename A1>
    Vector &forEach_i(FN fn, A1 a1) {
        for (size_t i = 0; i < this->size(); ++i) {
            fn((*this)[i], i, a1);
        }
        return *this;
    }
    template <typename FN, typename A1, typename A2>
    Vector &forEach_i(FN fn, A1 a1, A2 a2) {
        for (size_t i = 0; i < this->size(); ++i) {
            fn((*this)[i], i, a1, a2);
        }
        return *this;
    }
    template <typename FN, typename A1, typename A2, typename A3>
    Vector &forEach_i(FN fn, A1 a1, A2 a2, A3 a3) {
        for (size_t i = 0; i < this->size(); ++i) {
            fn((*this)[i], i, a1, a2, a3);
        }
        return *this;
    }

    // --- forEachX: like forEach_i but with a rich state struct ---
    template <typename FN>
    Vector &forEachX(FN fn) {
        for (size_t i = 0; i < this->size(); ++i) {
            FEstate<Vector<T> > st(i, i == 0, i == this->size() - 1, *this);
            fn((*this)[i], st);
        }
        return *this;
    }
    template <typename FN, typename A1>
    Vector &forEachX(FN fn, A1 a1) {
        for (size_t i = 0; i < this->size(); ++i) {
            FEstate<Vector<T> > st(i, i == 0, i == this->size() - 1, *this);
            fn((*this)[i], st, a1);
        }
        return *this;
    }
    template <typename FN, typename A1, typename A2>
    Vector &forEachX(FN fn, A1 a1, A2 a2) {
        for (size_t i = 0; i < this->size(); ++i) {
            FEstate<Vector<T> > st(i, i == 0, i == this->size() - 1, *this);
            fn((*this)[i], st, a1, a2);
        }
        return *this;
    }
    template <typename FN, typename A1, typename A2, typename A3>
    Vector &forEachX(FN fn, A1 a1, A2 a2, A3 a3) {
        for (size_t i = 0; i < this->size(); ++i) {
            FEstate<Vector<T> > st(i, i == 0, i == this->size() - 1, *this);
            fn((*this)[i], st, a1, a2, a3);
        }
        return *this;
    }

    template <typename FN, typename A1, typename A2, typename A3, typename A4>
    Vector &forEachX(FN fn, A1 a1, A2 a2, A3 a3, A4 a4) {
        for (size_t i = 0; i < this->size(); ++i) {
            FEstate<Vector<T> > st(i, i == 0, i == this->size() - 1, *this);
            fn((*this)[i], st, a1, a2, a3, a4);
        }
        return *this;
    }

    Vector &printEach(std::string separator = ",") {
        for (size_t i = 0; i < this->size(); ++i) {
            std::string sep = (i == this->size() - 1) ? "" : separator; // no separator after last element
            printx("\033[100m", (*this)[i],RESET, sep);
        }
        print();
        return *this;
    }

    template <typename FN>
    Vector &printEach(FN fn) {
        for (size_t i = 0; i < this->size(); ++i) {
            fn((*this)[i], i, i == 0, i == this->size() - 1);
        }
        return *this;
    }

        template <typename FN, typename A1>
    Vector &printEach(FN fn, A1 a1) {
        for (size_t i = 0; i < this->size(); ++i) {
            fn((*this)[i], i, i == 0, i == this->size() - 1, a1);
        }
        return *this;
    }

            template <typename FN, typename A1, typename A2>
    Vector &printEach(FN fn, A1 a1, A2 a2) {
        for (size_t i = 0; i < this->size(); ++i) {
            fn((*this)[i], i, i == 0, i == this->size() - 1, a1, a2);
        }
        return *this;
    }
    



    // --- nothing: no-op that returns itself (ignores its argument) ---
    template <typename U>
    Vector& nothing(U) {
        return *this;
    }

    // --- nothing: no-op that returns itself (ignores its argument) ---
    template <typename FN>
    Vector& log(FN fn) {
        fn(*this);
        return *this;
    }

        // --- nothing: no-op that returns itself (ignores its argument) ---
    template <typename FN, typename A1>
    Vector& log(FN fn, A1 a1) {
        fn(*this, a1);
        return *this;
    }

    template <typename FN, typename A1, typename A2>
    Vector& log(FN fn, A1 a1, A2 a2) {
        fn(*this, a1, a2);
        return *this;
    }

    // --- reverse: return a new vector with elements in reverse order ---
    Vector reverse() const {
        Vector result;
        for (size_t i = this->size(); i > 0; --i)
            result.add((*this)[i - 1]);
        return result.ok();
    }

    // --- orderBy: reorder elements according to an index mapping ---
    // Usage: Vector<T> reordered = original.orderBy(orderMap);
    // where orderMap[i] is the index into original for position i in the result.
    Vector orderBy(const Vector<int>& order) const {
        Vector result;
        for (size_t i = 0; i < order.size(); ++i)
            result.add((*this)[order[i]]);
        return result.ok();
    }

    // --- orderBy: reorder elements by identity matching ---
    // Usage: Vector<T> reordered = original.orderBy(newOrder, accessIdentity);
    // For each newOrder[i], finds original[j] where accessIdentity(original[j]) == accessIdentity(newOrder[i])
    template <typename ORDER_VEC, typename FN>
    Vector orderBy(const ORDER_VEC& order, FN accessIdentity) const {
        Vector result;
        for (size_t i = 0; i < order.size(); ++i) {
            for (size_t j = 0; j < this->size(); ++j) {
                if (accessIdentity((*this)[j]) == accessIdentity(order[i])) {
                    result.add((*this)[j]);
                    break;
                }
            }
        }
        return result.ok();
    }
};

#endif // VECTOR_HPP
