<?php

// https://github.com/KnpLabs/php-github-api
require_once "php-github-api/vendor/autoload.php";

include "private.php";

function getMembers()
{
	$organizationClient = new \Github\Client();
	$organizationClient->authenticate($organizationToken, null, \Github\Client::AUTH_HTTP_TOKEN);

	$result = $organizationClient->api("organizations")->teams()->all("SFML");

	$teams = [];

	foreach($result as $team)
		$teams[$team["name"]] = $team["id"];

	$result = $organizationClient->api("organizations")->teams()->members($teams["SFML"]);

	$members = [];

	foreach($result as $member)
		$members[] = $member["login"];

	return $members;
}

function getBuildParameters($prId)
{
	$buildBotClient = new \Github\Client();
	$buildBotClient->authenticate($buildBotToken, null, \Github\Client::AUTH_HTTP_TOKEN);

	try
	{
		$pullRequest = $buildBotClient->api("pull_request")->show("SFML", "SFML", $prId);

		return array("repository" => $pullRequest["head"]["repo"]["full_name"], "branch" => $pullRequest["head"]["ref"]);
	}
	catch(Exception $e)
	{
	}

	return array("repository" => "", "branch" => "");
}

function getBuildRequest($data)
{
	if((!array_key_exists("action", $data)) || ($data["action"] != "created"))
		return array("id" => 0, "user" => "");

	if((!array_key_exists("issue", $data)) || (!array_key_exists("number", $data["issue"])))
		return array("id" => 0, "user" => "");

	$number = $data["issue"]["number"];

	if((!array_key_exists("comment", $data)) || (!array_key_exists("user", $data["comment"])) || (!array_key_exists("login", $data["comment"]["user"])))
		return array("id" => 0, "user" => "");

	$user = $data["comment"]["user"]["login"];

	if(!in_array($user, getMembers()))
		return array("id" => 0, "user" => "");

	if((!array_key_exists("comment", $data)) || (!array_key_exists("body", $data["comment"])))
		return array("id" => 0, "user" => "");

	if(strpos($data["comment"]["body"], "SFMLBuildMaster: Build this please.") !== false)
		return array("id" => $number, "user" => $user);

	return array("id" => 0, "user" => "");
}

function main()
{
	$request = getBuildRequest(json_decode(file_get_contents("php://input"), true));

	if($request["id"] != 0)
	{
		$buildParameters = getBuildParameters($request["id"]);

		if(!empty($buildParameters["repository"]) && !empty($buildParameters["branch"]))
		{
			$user = $request["user"];
			$branch = $buildParameters["branch"];
			$repository = $buildParameters["repository"];
			$comment = "Starting build requested by $user for $branch on $repository.";

			$data = array(
				"repository" => "https://github.com/$repository.git",
				"project" => "SFML",
				"branch" => $branch,
				"comments" => $comment,
				"author" => $user
			);

			$options = array(
				"http" => array(
					"header"  => "Content-type: application/x-www-form-urlencoded\r\n",
					"method"  => "POST",
					"content" => http_build_query($data)
				)
			);

			$context = stream_context_create($options);
			$result = file_get_contents($url, false, $context);

			print("<html><head><title>Build started.</title></head><body>Build started.</body></html>");
			return;
		}
	}

	print("<html><head><title>Build not started.</title></head><body>Build not started.</body></html>");
}

main();

?>