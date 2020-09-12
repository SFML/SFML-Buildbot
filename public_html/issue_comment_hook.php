<?php

function checkPullRequestData($data)
{
	if((!array_key_exists("head", $data)) || (!array_key_exists("user", $data["head"])) || (!array_key_exists("login", $data["head"]["user"])))
		return false;

	if((!array_key_exists("head", $data)) || (!array_key_exists("sha", $data["head"])))
		return false;

	return true;
}

function checkBuildRequest($data)
{
	if((!array_key_exists("issue", $data)) || (!array_key_exists("pull_request", $data["issue"])) || (!array_key_exists("url", $data["issue"]["pull_request"])))
		return false;

	if((!array_key_exists("action", $data)) || ($data["action"] != "created"))
		return false;

	if((!array_key_exists("issue", $data)) || (!array_key_exists("number", $data["issue"])))
		return false;

	if((!array_key_exists("comment", $data)) || (!array_key_exists("user", $data["comment"])) || (!array_key_exists("login", $data["comment"]["user"])))
		return false;

	if((!array_key_exists("comment", $data)) || (!array_key_exists("author_association", $data["comment"])) || ($data["comment"]["author_association"] != "MEMBER"))
		return false;

	if((!array_key_exists("comment", $data)) || (!array_key_exists("body", $data["comment"])))
		return false;

	if(strpos($data["comment"]["body"], "SFMLBuildMaster: Build this please.") === false)
		return false;

	return true;
}

function main()
{
	$json = json_decode(file_get_contents("php://input"), true);

	if(!checkBuildRequest($json))
	{
		print("<html><head><title>Issue Comment Hook</title></head><body>Build not started, build request check failed.</body></html>");

		return;
	}

	$options = array(
		"http" => array(
			"user_agent" => "SFML BuildBot"
		)
	);

	$prjson = json_decode(file_get_contents($json["issue"]["pull_request"]["url"], false, stream_context_create($options)), true);

	if(!checkPullRequestData($prjson))
	{
		print("<html><head><title>Issue Comment Hook</title></head><body>Build not starte, pull request data check failed.</body></html>");

		return;
	}

	$id = $json["issue"]["number"];
	$user = $json["comment"]["user"]["login"];
	$author = $prjson["head"]["user"]["login"];
	$branch = "refs/pull/$id/head";
	$revision = $prjson["head"]["sha"];
	$repository = "SFML/SFML";
	$comment = "Starting build requested by $user for pull request #$id on $repository.";
	$category = "PR";

	$data = array(
		"repository" => "https://github.com/$repository.git",
		"project" => $repository,
		"branch" => $branch,
		"revision" => $revision,
		"comments" => $comment,
		"author" => $author,
		"category" => $category
	);

	$socket = stream_socket_client('unix:///home/buildbot/buildbot.sock', $errno, $errst, 4);

	$payload = http_build_query($data);
	$payloadlength = strlen($payload);

	$file = fopen("../changehook.passwd", "r");

	if($file === false)
	{
		print("<html><head><title>Issue Comment Hook</title></head><body>Build not started, cannot get changehook authentication data.</body></html>");

		return;
	}

	preg_match('/([^:\s]*):([^:\s]*)/', fgets($file), $matches);
	fclose($file);

	$auth = base64_encode($matches[1] . ":" . $matches[2]);

	$socketdata = "";
	$socketdata .= "POST /change_hook/base HTTP/1.1\r\n";
	$socketdata .= "Host: ci.sfml-dev.org\r\n";
	$socketdata .= "Authorization: Basic $auth\r\n";
	$socketdata .= "Content-type: application/x-www-form-urlencoded\r\n";
	$socketdata .= "Content-Length: $payloadlength\r\n";
	$socketdata .= "Connection: close\r\n\r\n";

	fwrite($socket, $socketdata);
	fwrite($socket, $payload);
	fclose($socket);

	print("<html><head><title>Issue Comment Hook</title></head><body>Build started.</body></html>");
}

main();

?>