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
    testing($script);
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

function process_parse_tests(){
    echo "Parse tests\n";
}

function process_interpret_tests(){
    echo "Interpret tests\n";
}

function testing($script){

    if ($script->isParseTests()){
        process_parse_tests();
    }
    if ($script->isIntTests()){
        process_interpret_tests();
    }

}

