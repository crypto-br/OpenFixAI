```java
import java.security.SecureRandom;

public class App {
  public static void main(String[] args) {
    SecureRandom random = new SecureRandom();
    int num = random.nextInt();
    System.out.println("Secure random number is: " + num);
  }
}
```