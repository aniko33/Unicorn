import javafx.application.Application;
import javafx.scene.Group
import javafx.scene.Scene
import javafx.scene.paint.Color
import javafx.stage.Stage

fun main() {
    Application.launch(App::class.java)
}

class App: Application() {
    override fun start(stage: Stage) {
        val root = Group()

        val scene = Scene(root, Color.WHITE)

        stage.scene = scene

        stage.show()
    }
}

