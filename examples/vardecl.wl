func main() -> int is
begin
    var a: int = 6;
    var b: int;
    begin
        b = 5;
        var c: int = b;
        const _01INTERNAL_CONST: int = c + 36;
    end
    return a + _01INTERNAL_CONST - b;
end func