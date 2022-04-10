<?php

/***
 * Projekt : IPP projekt, časť č.2 (Test PHP 8.1)
 * @file test.php
 * @author Kristián Kičinka (xkicin02)
 */

use JetBrains\PhpStorm\NoReturn;

ini_set('display_errors','stderr');

require_once("Script.php");
require_once("TestObject.php");
require_once("TestProcess.php");
require_once("Output.php");

const ARG_ERROR = 10;
const FILE_ERROR = 41;
const FILE_SEPARATOR = "/";

main($argc, $argv);

function main($argc, $argv){
    $script = new Script();
    array_shift($argv);
    process_arguments($argc, $argv, $script);
    $tests = load_tests($script);
    process_extensions($tests);
    testing($tests, $script);
}

function close_script($code){
    switch ($code){
        case ARG_ERROR:
            echo "Arguments error!\n";
            break;
        case FILE_ERROR:
            echo "File error!\n";
            break;
    }
    exit($code);
}

function process_arguments($argc, $argv, $script){
    if ($argc > 1){
        foreach($argv as $arg){
            switch ($arg){
                case "--help":
                    echo "Help function\n";
                    exit(0);
                case (bool)preg_match("'^--directory=(.+)$'", $arg, $results):
                    $script->setDirectoryPath($results[1]);
                    break;
                case "--recursive":
                    $script->setRecursive(true);
                    break;
                case (bool)preg_match("'^--parse-script=(.+)$'", $arg, $results):
                    $script->setParseScriptFile($results[1]);
                    break;
                case (bool)preg_match("'^--int-script=(.+)$'", $arg, $results):
                    $script->setIntScriptFile($results[1]);
                    break;
                case "--parse-only":
                    $script->setIntTests(false);

                    break;
                case "--int-only":
                    $script->setParseTests(false);
                    break;
                case (bool)preg_match("'^--jexampath=(.+)$'", $arg, $results):
                    $script->setJexamPath($results[1]);
                    break;
                case "--noclean":
                    $script->setNoclean(true);
                    break;
                default :
                    close_script(10);
            }
        }
    }else{
        close_script(10);
    }
}

function scan_directory($directory_path, $script){
    $files_list = [];

    $dir_content = scandir($directory_path);
    foreach ($dir_content as $item){

        if ($item == "." or $item == ".." or ""){
            continue;
        }
        $file_path = $directory_path.FILE_SEPARATOR.$item;

        if (is_dir($file_path)){
            if ($script->isRecursive() == true){
                array_push($files_list, ...scan_directory($file_path, $script));
            }
        }else{
            $files_list[] = pathinfo($file_path);
        }
    }
    return $files_list;
}

function load_tests($script){

    $directory_path = $script->getDirectoryPath();
    $tests_list = [];
    $test_files_list = scan_directory($directory_path, $script);

    foreach ($test_files_list as $test_file){
        $name  = $test_file["filename"];
        $directory_path = $test_file["dirname"];
        $file_path = $directory_path.FILE_SEPARATOR.$name;
        $extension = $test_file["extension"];

        if (!in_array($extension,["src","in","out","rc"])){
            continue;
        }

        if (!array_key_exists($file_path, $tests_list)){
            $tests_list[$file_path] = new TestObject($name, $directory_path, $file_path);
        }

        switch ($extension){
            case "src":
                $tests_list[$file_path]->setSrcFile(true);
                break;
            case "in":
                $tests_list[$file_path]->setInFile(true);
                break;
            case "out":
                $tests_list[$file_path]->setOutFile(true);
                break;
            case "rc":
                $tests_list[$file_path]->setRcFile(true);
                break;
        }

    }

    return $tests_list;

}

function process_extensions($tests){
    foreach ($tests as $test){

        if (!$test->isSrcFile()){
            close_script(FILE_ERROR);
        }
        if (!$test->isInFile()){
            file_put_contents($test->getTestFilePath().".in",'');
        }
        if (!$test->isOutFile()){
            file_put_contents($test->getTestFilePath().".out",'');
        }
        if (!$test->isRcFile()){
            file_put_contents($test->getTestFilePath().".rc",'0');
        }
    }
}

function load_rc_number($test){
    $rc_file = $test->getTestFilePath().".rc";
    $rc = file_get_contents($rc_file);
    return $rc;
}

function process_parse_test($test, $script){
    $process_name = $test->getTestName();
    $process_type = "parse";

    $src_file = $test->getTestFilePath().".src";
    $out_file = $test->getTestFilePath().".tmp_parse_out";
    $err_file = $test->getTestFilePath().".tmp_parse_err";

    $test_process = new TestProcess($process_type, $process_name, $src_file);
    $test_process->setTmpErrFilePath($err_file);
    $test_process->setTmpOutFilePath($out_file);

    $php_command = "php ".$script->getParseScriptFile()." <".$src_file." 2>".$err_file." 1>".$out_file;

    exec($php_command, $output, $returned_code);

    $test_process->setExpectedExitCode(load_rc_number($test));
    $test_process->setReturnedExitCode($returned_code);

    if ($returned_code != 0){

        if ($returned_code == $test_process->getExpectedExitCode()){
            $test_process->setTestPassed(true);
            $script->incPassedTestCount();
        }
        else{
            $test_process->setTestPassed(false);
            $script->incFailedTestCount();
        }

        return $test_process;
    }

    $expected_out = $test->getTestFilePath().".out";
    $jexam_jar = $script->getJexamPath().FILE_SEPARATOR."jexamxml.jar";
    $jexam_options = $script->getJexamPath().FILE_SEPARATOR."options";
    $jexam_exec = "java -jar ".$jexam_jar." ".$out_file." ".$expected_out." diffs.xml  /D ".$jexam_options;

    exec($jexam_exec, $output, $returned_code_cmp);
    @unlink("diffs.xml");

    if ($returned_code_cmp != 0){
        $test_process->setSameOutput(false);
        $test_process->setTestPassed(false);
        $script->incFailedTestCount();
    }else{
        $test_process->setSameOutput(true);
        $test_process->setTestPassed(true);
        $script->incPassedTestCount();
    }

    return $test_process;
}

function process_interpret_test($test, $script, $parse_tests, $key){

    $process_name = $test->getTestName();
    $process_type = "interpret";

    if (!array_key_exists($key, $parse_tests)){
        $src_file = $test->getTestFilePath().".src";
    }else{
        $src_file = $parse_tests[$key]->getTmpOutFilePath();
    }

    $out_file = $test->getTestFilePath().".tmp_int_out";
    $err_file = $test->getTestFilePath().".tmp_int_err";
    $input_file = $test->getTestFilePath().".in";
    $out_int_file = $test->getTestFilePath().".out";

    $test_process = new TestProcess($process_type, $process_name, $src_file);

    $test_process->setTmpOutFilePath($out_file);
    $test_process->setTmpErrFilePath($err_file);

    $python_exec = "python3 ".$script->getIntScriptFile()." --source=".$src_file.
                    " <".$input_file." 2>".$err_file." 1>".$out_file;

    exec($python_exec, $output, $returned_code);

    $test_process->setExpectedExitCode(load_rc_number($test));
    $test_process->setReturnedExitCode($returned_code);

    if ($returned_code != 0){

        if ($returned_code == $test_process->getExpectedExitCode()){
            $test_process->setTestPassed(true);
            $script->incPassedTestCount();
        }
        else{
            $test_process->setTestPassed(false);
            $script->incFailedTestCount();
        }

        return $test_process;
    }

    $diff_exec = "diff ".$out_int_file." ".$out_file;
    exec($diff_exec, $output, $returned_code_cmp);

    if ($returned_code_cmp != 0){
        $test_process->setSameOutput(false);
        $test_process->setTestPassed(false);
        $script->incFailedTestCount();
    }else{
        $test_process->setSameOutput(true);
        $test_process->setTestPassed(true);
        $script->incPassedTestCount();
    }

    return $test_process;

}

function testing($tests, $script){
    $parse_tests = [];
    $interpret_tests = [];

    foreach ($tests as $test){
        $key = $test->getTestFilePath();
        if ($script->isParseTests()){

            $parse_tests[$key] = process_parse_test($test, $script);
            $script->incTotalTestCount();

        }
        if ($script->isIntTests()){
            $interpret_tests[$key] = process_interpret_test($test, $script, $parse_tests, $key);
            $script->incTotalTestCount();
        }
    }

    $script->setPercentage();
    (new Output)->generateTemplate($script);
}

