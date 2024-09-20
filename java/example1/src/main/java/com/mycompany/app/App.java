```java
import java.security.SecureRandom;

public class Main {
    public static void main(String[] args) {
        SecureRandom random = new SecureRandom();
        int num = random.nextInt();
        System.out.println("Número aleatório gerado: " + num);
    }
}
```