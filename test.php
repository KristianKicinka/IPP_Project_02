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
const FILE_SEPARATOR = "/";

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

class Test{

    private String $test_name;
    private String $test_directory_path;
    private String $test_file_path;

    private bool $src_file;
    private bool $out_file;
    private bool $in_file;
    private bool $rc_file;

    public function __construct($test_name, $test_directory_path, $test_file_path){
        $this->test_name = $test_name;
        $this->test_directory_path = $test_directory_path;
        $this->test_file_path = $test_file_path;

        $this->src_file = false;
        $this->out_file = false;
        $this->in_file = false;
        $this->rc_file = false;
    }

    public function getTestName(): string {
        return $this->test_name;
    }

    public function setTestName(string $test_name): void {
        $this->test_name = $test_name;
    }

    public function getTestDirectoryPath(): string {
        return $this->test_directory_path;
    }

    public function setTestDirectoryPath(string $test_directory_path): void {
        $this->test_directory_path = $test_directory_path;
    }

    public function getTestFilePath(): string {
        return $this->test_file_path;
    }

    public function setTestFilePath(string $test_file_path): void {
        $this->test_file_path = $test_file_path;
    }

    public function isSrcFile(): bool {
        return $this->src_file;
    }

    public function setSrcFile(bool $src_file): void {
        $this->src_file = $src_file;
    }

    public function isOutFile(): bool {
        return $this->out_file;
    }

    public function setOutFile(bool $out_file): void {
        $this->out_file = $out_file;
    }

    public function isInFile(): bool {
        return $this->in_file;
    }

    public function setInFile(bool $in_file): void {
        $this->in_file = $in_file;
    }

    public function isRcFile(): bool {
        return $this->rc_file;
    }

    public function setRcFile(bool $rc_file): void {
        $this->rc_file = $rc_file;
    }

}

main($argc, $argv);

function main($argc, $argv){
    $script = new Script();
    array_shift($argv);
    process_arguments($argc, $argv, $script);
    $tests = load_tests($script);
    process_extensions($tests);
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

function scan_directory($directory_path, $script){
    $files_list = [];

    $dir_content = scandir($directory_path);
    foreach ($dir_content as $item){

        if ($item == "." or $item == ".." or ""){
            continue;
        }
        $file_path = $directory_path.FILE_SEPARATOR.$item;

        if (is_dir($file_path)){
            if ($script->get_recursive() == true){
                array_push($files_list, ...scan_directory($file_path, $script));
            }
        }else{
            $files_list[] = pathinfo($file_path);
        }
    }
    return $files_list;
}

function load_tests($script){

    $directory_path = $script->get_directory_path();
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
            $tests_list[$file_path] = new Test($name, $directory_path, $file_path);
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
            file_put_contents($test->getTestFilePath().".rc",0);
        }
    }
}

