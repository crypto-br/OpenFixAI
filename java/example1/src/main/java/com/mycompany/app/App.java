```java
import java.security.SecureRandom;

public class MyClass {
    public void method() {
        SecureRandom rnd = new SecureRandom();
        int n = rnd.nextInt();
        // ...
    }
}
```