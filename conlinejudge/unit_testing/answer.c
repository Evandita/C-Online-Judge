#include <stdio.h>

int main(void){
    int a, b;
    scanf("%d", &a);
    scanf("%d", &b);

    if (a > b){
        printf("A");
    }
    else if (a < b) {
        printf("B");
    }
    else {
        printf("BEBAS");
    }
    return 0;
}