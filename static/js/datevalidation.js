function validateDate() {
  let hi = document.forms["addperiod"]["inihour"].value;
  let mi = document.forms["addperiod"]["inimin"].value;
  let hf = document.forms["addperiod"]["fimhour"].value;
  let mf = document.forms["addperiod"]["fimmin"].value;

  let ininumb = parseInt(hi) * 60 + parseInt(mi)
  let fimnumb = parseInt(hf) * 60 + parseInt(mf)

  if (ininumb >= fimnumb){
     alert("Horario incial deve ser menor que o final")
     return false
  }
}