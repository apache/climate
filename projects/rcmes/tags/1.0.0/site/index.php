<?php
/**
 * Copyright (c) 2010, California Institute of Technology.
 * ALL RIGHTS RESERVED. U.S. Government sponsorship acknowledged.
 * 
 * $Id$
 * 
 * 
 * OODT Balance
 * Web Application Base Framework
 * 
 * Front-controller
 * This file handles the marshalling of requests to the appropriate
 * application view. 
 * 
 * @author ahart
 * 
 */
// Change this to false for production environments
define ("DEBUG", true);

/* Set up application environment ************************************/
require_once("./webapp-base/classes/bootstrap.php");

/* Route the request to the appropriate view *************************/
$pageInfo = $app->route($request);

/* Generate a response to the request ********************************/
$response = $app->getResponse($pageInfo);

/* Send the response out to the user *********************************/
$response->send();

/* Clean up after ourselves ******************************************/
$app->cleanup();