```java
import java.security.SecureRandom;

public class Main {
public static void main(String[] args) {
    SecureRandom secureRandom = new SecureRandom();
    int randomInt = secureRandom.nextInt();
    System.out.println("Randomly generated secure int: " + randomInt);
    }
}
```