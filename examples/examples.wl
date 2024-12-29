func main() -> int is
begin
	return 1 + 2;
end func

////

import io;

func main() -> none is
begin
	var a: float = 1;
	var b: float = 2;
	io.writeln(a + b);
	io.writeln("Hello, world!");
end func

////

import io;

func derivative(x: float, delta: float, f: float -> float) -> float is
	return (f(x + delta) - f(x)) / delta;

func main() -> none is
begin
    const c: float = 5.0
	var xsquare: float -> float is (x) {
	    return x^2 + c;
	}
	var d: float = derivative(6, 1e-6, xsquare);
	io.writeln(d);
end func

////

import io;

struct Dog is
	name: str
	breed: str
end struct

func Dog.bark(self) -> none is
	io.writeln("Woof! I'm %s, a %s!", self.name, self.breed);

func main() -> none is
begin
	var rene: Dog = Dog {
	    name = "René",
		breed = "dragon"
	};
	rene.bark();
end func

////

import io;

interface CanSpeak is
begin
    func speak(self) -> void;
end interface

interface Hops is
    func hop(self) -> void;

struct Cat impl CanSpeak, Hops is
    name: str
end struct

func Cat.speak(self) -> void is
    io.writeln("Meow! I'm %s, a kitty!", self.name);

func Cat.hop(self) -> void is
    io.wirteln("hopping around cutely");

func main() -> none is
begin
    var ladon = Cat {
	    name = "Ladon"
	};
	ladon.speak();
	ladon.hop();
end func