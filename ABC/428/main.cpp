#include <format>
#include <print>

int main() {
    int a = 3, b = 4;
    std::print("a = {}, b = {}\n", a, b);
    auto s = std::format("sum = {}", a + b);
    std::print("{}\n", s);
}