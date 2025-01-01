func main() -> int is
begin
    var a: int = 6;
    var b: int;
    begin
        b = 3;
        var c: int = b;
        b = c + 2;
    end
    const _01INTERNAL_CONST: int = b + 36;
    return a + _01INTERNAL_CONST - b;
end func