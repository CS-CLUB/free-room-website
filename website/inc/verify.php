<?php
/*
 *  Free Room Finder
 *
 *  Copyright (C) 2013 Jonathan Gillett and Joseph Heron 
 *  All rights reserved.
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

require_once "db_interface.php";


/**
 * A function which returns a login session string which is the
 * session username encrypted with AES256 and then encoded with base64
 * 
 * @param string $username The username of the person logged in
 * @param string $SESSION_KEY The session encrypt/decrypt key
 * @return string The generated login session for the user
 */
function generate_session($username, $SESSION_KEY) 
{
        return trim(base64_encode(mcrypt_encrypt(MCRYPT_RIJNDAEL_256, 
                    $SESSION_KEY, $username, MCRYPT_MODE_ECB, 
                    mcrypt_create_iv(mcrypt_get_iv_size(MCRYPT_RIJNDAEL_256, 
                    MCRYPT_MODE_ECB), MCRYPT_RAND))));
}


/**
 * As the session login/cookie contain the username encrypted with AES256 and then encoded
 * with base64, get the username from the session login/cookie by decrypting the data.
 * 
 * NOTE: This method is primarily used to get the username from a valid login cookie
 *
 * @param mysqli $mysqli_conn The mysqli connection object for the free room finder DB
 * @param string $ses_validate The session data to validate
 * @param string $SESSION_KEY The session encrypt/decrypt key
 * @return string The username stored in the session login/cookie
 */
function username_from_session($mysqli_conn, $ses_validate, $SESSION_KEY)
{
	global $user_table;
    /* Decrypted validate session variable */
    $validate = trim(mcrypt_decrypt(MCRYPT_RIJNDAEL_256, $SESSION_KEY, base64_decode($ses_validate),
            MCRYPT_MODE_ECB, mcrypt_create_iv(mcrypt_get_iv_size(MCRYPT_RIJNDAEL_256,
                    MCRYPT_MODE_ECB), MCRYPT_RAND)));
    
    $username = '';
    
    /* Get the candidate for the current position from the database */
    if ($stmt = $mysqli_conn->prepare("SELECT username
                                                FROM " . $user_table .
                                                " WHERE username LIKE ?" ))
    {
        /* bind parameters for markers */
        $stmt->bind_param('s', $validate);

        /* execute query */
        $stmt->execute();

        /* bind result variables */
        $stmt->bind_result($username);

        $stmt->fetch();

        /* close statement */
        $stmt->close();
    }

    /* If username found, session is valid */
    if (strcasecmp($validate, $username) === 0)
    {
        return $username;
    }

    /* Session invalid! */
    return '';
}

/** 
 * A function which verifies the login information provided by the user
 * returns true if the login username and password provided are valid
 * 
 * @param mysqli $mysqli_conn The mysqli connection object for the free room finder DB
 * @param string $username The username of the person logging in
 * @param string $password The password of the person logging in
 * @param string $AES_KEY The AES encrypt/decrypt key for the password
 * @return boolean True if the login information provided is valid
 */
function verify_login($mysqli_conn, $username, $password, $AES_KEY)
{
	global $user_table;
	
    $user_match = '';
    $pass_match = '';
    
    /* Get the username from the database if it exists */
    if ($stmt = $mysqli_conn->prepare("SELECT username FROM "
                                                . $user_table . 
                                                " WHERE username LIKE ?"))
    {
        /* bind parameters for markers */
        $stmt->bind_param('s', $username);

        /* execute query */
        $stmt->execute();

        /* bind result variables */
        $stmt->bind_result($user_match);

        /* fetch value */
        $stmt->fetch();

        /* close statement */
        $stmt->close();
    }
    
    /* If username found, verify the password provided for that username */
    if (strcasecmp($username, $user_match) === 0)
    {
        if ($stmt = $mysqli_conn->prepare("SELECT AES_DECRYPT(password, ?) FROM ". $user_table ." WHERE username LIKE ?"))
        {
            /* bind parameters for markers */
            $stmt->bind_param('ss', $AES_KEY, $username);

            /* execute query */
            $stmt->execute();

            /* bind result variables */
            $stmt->bind_result($pass_match);

            $stmt->fetch();

            /* close statement */
            $stmt->close();
        }

        /* Verify the password, remove the salt from password stored in DB */
        if (strcmp($password, substr($pass_match, 8)) === 0)
        {
            return true;
        }
    }

    /* Invalid username or password or both */
    return false;
}

/** 
 * A function which validates the session by decrypting the validate session
 * variable and comparing it to the username session variable
 * 
 * @param mysqli $mysqli_conn The mysqli connection object for the free room finder DB
 * @param string $ses_validate The session data to validate
 * @param string $SESSION_KEY The session encrypt/decrypt key
 * @return boolean true if the decrypted validate session variable matches the
 * username stored in the database
 *
 */
function verify_login_session($mysqli_conn, $ses_validate, $SESSION_KEY)
{
	global $user_table;
	
    /* Decrypted validate session variable */ 
    $validate = trim(mcrypt_decrypt(MCRYPT_RIJNDAEL_256, $SESSION_KEY, base64_decode($ses_validate), 
                MCRYPT_MODE_ECB, mcrypt_create_iv(mcrypt_get_iv_size(MCRYPT_RIJNDAEL_256, 
                MCRYPT_MODE_ECB), MCRYPT_RAND)));
    $user_match = '';
    
    /* Get the username from the database if it exists */
    if ($stmt = $mysqli_conn->prepare("SELECT username FROM "
                                                . $user_table . 
                                                " WHERE username LIKE ?"))
    {
        /* bind parameters for markers */
        $stmt->bind_param('s', $validate);
    
        /* execute query */
        $stmt->execute();
    
        /* bind result variables */
        $stmt->bind_result($user_match);
    
        /* fetch value */
        $stmt->fetch();
    
        /* close statement */
        $stmt->close();
    }
    
    /* If username found, session is valid */
    if (strcasecmp($validate, $user_match) === 0)  
    {
        return true;
    }
    
    /* Session invalid! */  
    return false;
}

/**
 * A function which sets the session data for a valid user who has logged in
 * to the free room website. It starts the session and stores the login
 * validation session variable, the username, access_account, and fullname
 * of the user.
 *
 * @param mysqli $mysqli_conn The mysqli connection object for the free room finder DB
 * @param string $username The username of the valid user who is logged in
 * @param string $SESSION_KEY The session encrypt/decrypt key
 */
function set_session_data($mysqli_conn, $username, $SESSION_KEY)
{   
    //TODO Determine the neccessary session data, copied from free-room_web
    /* Set session info validate is a unique session based on their username */
    $_SESSION['login'] = generate_session($username, $SESSION_KEY);
    
    /* Set the members session information */
    $user = get_user($mysqli_conn, $username);
    $_SESSION['username'] = $username;
    $_SESSION['access_account'] = $user['access_account'];
    $_SESSION['first_name'] = $user['first_name'];
    $_SESSION['last_name'] = $user['last_name'];
}

/**
 * A function which sets sets a login cookie in the users browser so that
 * they do not have to login each time they access the website. The login
 * cookie by default is set for one day.
 * 
 * NOTE: This method requires that the user has already logged into the
 * website with a valid account and that a login session has been created.
 * 
 * @return boolean TRUE If the cookie was set correctly in the user's browser
 */
function set_login_cookie()
{
    //TODO determine if the cookie is fine, copied from free room finder DB

    /* Verify the login session created and the cookie set successfully */
    if (isset($_SESSION['login']))
    {
        /*  Set a cookie for 1 day, content of cookie is their login session */
        if (setcookie('login', $_SESSION['login'], time()+60*60*24))
        {
            return true;
        }
    }
}


/**
 * A function which validates the login cookie, this verifies that the
 * login information set in the cookie is valid for the user, if it
 * is then the user is logged in.
 *
 * @param mysqli $mysqli_conn The mysqli connection object for the free room finder DB
 * @param string $SESSION_KEY The session encrypt/decrypt key
 * @return TRUE If the cookie is a valid login cookie
 */
function verify_login_cookie($mysqli_conn, $SESSION_KEY)
{
    //TODO verify that this function is valid, copied from free room finder DB
    /* Verify the login cookie is set and that the login is valid */
    if (isset($_COOKIE['login']))
    {
        /* Get the login cookie data */
        $login_cookie = htmlspecialchars($_COOKIE['login']);
        
        /* Validate the login cookie data, which contains the same data as session */
        if (verify_login_session($mysqli_conn, $login_cookie, $SESSION_KEY))
        {
            return true;
        }
    }
    
    return false;
}
?>