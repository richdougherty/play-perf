package controllers;

import play.*;
import play.mvc.*;

import views.html.*;

public class Application extends Controller {

  //@BodyParser.Of(BodyParser.Empty.class) FIXME: BodyParser.Empty
  public static Result helloworld() {
    return ok("Hello world");
  }

  //@BodyParser.Of(BodyParser.Empty.class) FIXME: BodyParser.Empty
  public static Result download(int length) {
    return ok(new byte[length]);
  }

  //@BodyParser.Of(BodyParser.Empty.class) FIXME: BodyParser.Empty
  public static Result downloadChunked(final int length) {

    Chunks<byte[]> chunks = new ByteChunks() {
      public void onReady(Chunks.Out<byte[]> out) {
        int remaining = length;
        int maxArraySize = 4 * 1024;
        while (remaining > 0) {
          int arraySize = Math.min(remaining, maxArraySize);
          byte[] array = new byte[arraySize];
          out.write(array);
          remaining -= arraySize;
        }
        out.close();
      }
    };

    // Serves this stream with 200 OK
    return ok(chunks);
  }

  @BodyParser.Of(BodyParser.Raw.class)
  public static Result upload() {
    return ok("upload"); // TODO: Verify upload happened
  }

}
