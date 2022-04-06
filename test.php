<?php

/***
 * Projekt : IPP projekt, časť č.2 (Test PHP 8.1)
 * @file test.php
 * @author Kristián Kičinka (xkicin02)
 */

use JetBrains\PhpStorm\NoReturn;

ini_set('display_errors','stderr');

const ARG_ERROR = 10;
const FILE_ERROR = 41;

class Script {
    private bool $recursive = false;
    private bool $parse_only = false;
    private bool $int_only = false;
    private bool $noclean = false;
    private $directory_path = null;
    private $jexam_path = null;
    private $parse_script_file = null;
    private $int_script_file = null;

    function get_recursive(): bool{
        return $this->recursive;
    }

    function get_parse_only(): bool{
        return $this->parse_only;
    }

    function get_int_only(): bool{
        return $this->int_only;
    }

    function get_noclean(): bool{
        return $this->noclean;
    }

    function get_directory_path(){
        return $this->directory_path;
    }

    function get_jexampath(){
        return $this->jexam_path;
    }

    function get_parse_script_file(){
        return $this->parse_script_file;
    }

    function get_int_script_file(){
        return $this->int_script_file;
    }

    function set_recursive($value){
        $this->recursive = $value;
    }

    function set_parse_only($value){
        $this->parse_only = $value;
    }

    function set_int_only($value){
        $this->int_only = $value;
    }

    function set_noclean($value){
        $this->noclean = $value;
    }

    function set_directory_path($path){
        $this->directory_path = $path;
    }

    function set_jexampath($path){
        $this->jexam_path = $path;
    }

    function set_parse_script_file($file_path){
        $file = fopen($file_path, "r") or close_script(FILE_ERROR);
        $this->parse_script_file = $file;
    }

    function set_int_script_file($file_path){
        $file = fopen($file_path, "r") or close_script(FILE_ERROR);
        $this->int_script_file = $file;
    }
}

main($argc, $argv);

function main($argc, $argv){
    $script = new Script();
    array_shift($argv);
    process_arguments($argc, $argv, $script);
    print $script->get_int_only().PHP_EOL;
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
                    $script->set_directory_path($results[1]);
                    break;
                case "--recursive":
                    $script->set_recursive(true);
                    break;
                case (bool)preg_match("'^--parse-script=(.+)$'", $arg, $results):
                    $script->set_parse_script_file($results[1]);
                    break;
                case (bool)preg_match("'^--int-script=(.+)$'", $arg, $results):
                    $script->set_int_script_file($results[1]);
                    break;
                case "--parse-only":
                    $script->set_parse_only(true);
                    break;
                case "--int-only":
                    $script->set_int_only(true);
                    break;
                case (bool)preg_match("'^--jexampath=(.+)$'", $arg, $results):
                    $script->set_jexampath($results[1]);
                    break;
                case "--noclean":
                    $script->set_noclean(true);
                    break;
                default :
                    close_script(10);
            }
        }
    }else{
        close_script(10);
    }
}
