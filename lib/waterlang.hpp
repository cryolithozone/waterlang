#include <string>

// This namespace represents objects of Waterlang.
// Currently, all classes (well one) that represents various types
// are simply wrappers over the C++ STL, which is extremely
// unideal, however I do not want to develop a second STL. Sorry.
// Perhaps "best" from mcy might be a better solution. We shall see.
namespace wl
{

// Type aliases. 
typedef signed long Int;
typedef double Float;
typedef const char* StringLiteral;

// Private namespace for various internals.
namespace {
    // This class represents a Waterlang object, from which every other
    // object inherits from. This sounds terrifying, but I'm just using this
    // to define a to_string method or something of the sort.
    class Value 
    {
        virtual char* to_string() = 0;
    };
}

// A Waterlang string.
// Wrapper over std::string. That's it. 
class String : Value
{
public:
    String(StringLiteral initializer) {
        data = std::string(initializer);
        size = data.length();
    }

    int Size() {
        return size;
    }

    virtual char* to_string() { return this->data.data(); }

private:
    std::string data;
    Int size;
};

}