re = new RegExp('[^a-zA-Z0-9_]');

function validateForm() {
  let x = document.forms["subirbase"]["dbname"].value;
  if (re.test(x)) {
    alert("Nome da base nao pode conter caracteres especiais");
    return false;
  }
}