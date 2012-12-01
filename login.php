<?php
/*
 *  Free Room Finder Website
 *
 *
 *  Authors -- Crow's Foot Group
 *  -------------------------------------------------------
 *
 *  Jonathan Gillett
 *  Joseph Heron
 *  Amit Jain
 *  Wesley Unwin
 *  Anthony Jihn
 * 
 *
 *  License
 *  -------------------------------------------------------
 *
 *  Copyright (C) 2012 Crow's Foot Group
 *
 *  This program is free software: you can redistribute it and/or modify
 *  it under the terms of the GNU Affero General Public License as
 *  published by the Free Software Foundation, either version 3 of the
 *  License, or (at your option) any later version.
 *
 *  This program is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU Affero General Public License for more details.
 *
 *  You should have received a copy of the GNU Affero General Public License
 *  along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

require_once "inc/db_interface.php";
require_once "inc/verify.php";
require_once "inc/free_room_auth.php";
require_once "inc/validate.php";


/* 1. User is not logged in, display one of the templates of logging in */
if (verify_login_cookie($mysqli_accounts, $SESSION_KEY) === false
	&& (!isset($_SESSION['login'])
	|| verify_login_session($mysqli_accounts, $_SESSION['login'], $SESSION_KEY) === false)
	&& !isset($_POST['login_username'])
	&& !isset($_POST['login_password']))
{
	include 'templates/header.php';
	include 'templates/login.php';
}
/* 2. User is not logged in and has submitted their login information */
elseif (verify_login_cookie($mysqli_accounts, $SESSION_KEY) === false
		&& (!isset($_SESSION['login'])
		|| verify_login_session($mysqli_accounts, $_SESSION['login'], $SESSION_KEY) === false)
		&& isset($_POST['login_username'])
		&& isset($_POST['login_password']))
{
	/* a) If the login information is valid and they entered the correct username/password  */
	if (validate_username($_POST['login_username']) && validate_password($_POST['login_password'])
		&& verify_login($mysqli_accounts, $_POST['login_username'] , $_POST['login_password'], $AES_KEY))
	{
		set_session_data($mysqli_accounts, $_POST['login_username'], $SESSION_KEY);
		
		if ($_POST['login_remember'] == 1)
		{
			set_login_cookie();
		}
		
		/* Redirect to the room_request page */
		header('Location: room_request.php');
	}
	/* b) The login information is invalid dislpay the invalid login page */
	else
	{
		include 'templates/header.php';
		include 'templates/invalid-login.php';
	}
}
else
{
	/* Redirect to room_request page */
	header('Location: room_request.php');
}

/* Include the footer */
include 'templates/footer.php';
exit();
?>