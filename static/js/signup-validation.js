function checkcpassword() {
		  
    
    var password = document.getElementById("password").value;
    var cpassword = document.getElementById("cpassword").value;

    if (password != cpassword) {

        $("#check_cpassword").html('Passwords do not match.');
        $("#submit").attr('disabled','disabled');
       

    } 
    else if(password == cpassword) {

        $("#check_cpassword").html('');
        $("#submit").attr('disabled',false);
    }
}