<?php

/***
 * Projekt : IPP projekt, časť č.2 (Test PHP 8.1)
 * @file Script.php
 * @author Kristián Kičinka (xkicin02)
 */

namespace objects;
use const FILE_SEPARATOR;

class Script
{

    private bool $recursive = false;
    private bool $parse_tests = true;
    private bool $int_tests = true;
    private bool $clean_files = true;

    private $directory_path;
    private $jexam_path;
    private $parse_script_file;
    private $int_script_file;

    private int $total_test_count;
    private int $passed_test_count;
    private int $failed_test_count;
    private int $percentage;

    public function __construct()
    {
        $this->directory_path = getcwd();
        $this->jexam_path = "/pub/courses/ipp/jexamxml/";
        $this->parse_script_file = getcwd() . FILE_SEPARATOR . "parse.php";
        $this->int_script_file = getcwd() . FILE_SEPARATOR . "interpret.py";
        $this->total_test_count = 0;
        $this->percentage = 0;
        $this->failed_test_count = 0;
        $this->passed_test_count = 0;

    }

    public function incTotalTestCount()
    {
        $this->total_test_count++;
    }

    public function incPassedTestCount()
    {
        $this->passed_test_count++;
    }

    public function incFailedTestCount()
    {
        $this->failed_test_count++;
    }

    public function setPercentage()
    {
        $this->percentage = intval(($this->passed_test_count / $this->total_test_count) * 100);
    }

    public function getPercentage()
    {
        return $this->percentage;
    }

    public function getFailedTestsCount()
    {
        return $this->failed_test_count;
    }

    /**
     * @return bool
     */
    public function isRecursive(): bool
    {
        return $this->recursive;
    }

    /**
     * @param bool $recursive
     */
    public function setRecursive(bool $recursive): void
    {
        $this->recursive = $recursive;
    }

    /**
     * @return bool
     */
    public function isParseTests(): bool
    {
        return $this->parse_tests;
    }

    /**
     * @param bool $parse_tests
     */
    public function setParseTests(bool $parse_tests): void
    {
        $this->parse_tests = $parse_tests;
    }

    /**
     * @return bool
     */
    public function isIntTests(): bool
    {
        return $this->int_tests;
    }

    /**
     * @param bool $int_tests
     */
    public function setIntTests(bool $int_tests): void
    {
        $this->int_tests = $int_tests;
    }

    /**
     * @return bool
     */
    public function isCleanFiles(): bool
    {
        return $this->clean_files;
    }

    /**
     * @param bool $clean_files
     */
    public function setCleanFiles(bool $clean_files): void
    {
        $this->clean_files = $clean_files;
    }

    /**
     * @return null
     */
    public function getDirectoryPath()
    {
        return $this->directory_path;
    }

    /**
     * @param null $directory_path
     */
    public function setDirectoryPath($directory_path): void
    {
        $this->directory_path = $directory_path;
    }

    /**
     * @return null
     */
    public function getJexamPath()
    {
        return $this->jexam_path;
    }

    /**
     * @param null $jexam_path
     */
    public function setJexamPath($jexam_path): void
    {
        $this->jexam_path = $jexam_path;
    }

    /**
     * @return null
     */
    public function getParseScriptFile()
    {
        return $this->parse_script_file;
    }

    /**
     * @param null $parse_script_file
     */
    public function setParseScriptFile($parse_script_file): void
    {
        $this->parse_script_file = $parse_script_file;
    }

    /**
     * @return null
     */
    public function getIntScriptFile()
    {
        return $this->int_script_file;
    }

    /**
     * @param null $int_script_file
     */
    public function setIntScriptFile($int_script_file): void
    {
        $this->int_script_file = $int_script_file;
    }

    /**
     * @return int
     */
    public function getTotalTestCount(): int
    {
        return $this->total_test_count;
    }

    /**
     * @param int $total_test_count
     */
    public function setTotalTestCount(int $total_test_count): void
    {
        $this->total_test_count = $total_test_count;
    }

    /**
     * @return int
     */
    public function getPassedTestCount(): int
    {
        return $this->passed_test_count;
    }

    /**
     * @param int $passed_test_count
     */
    public function setPassedTestCount(int $passed_test_count): void
    {
        $this->passed_test_count = $passed_test_count;
    }

    /**
     * @return int
     */
    public function getFailedTestCount(): int
    {
        return $this->failed_test_count;
    }

    /**
     * @param int $failed_test_count
     */
    public function setFailedTestCount(int $failed_test_count): void
    {
        $this->failed_test_count = $failed_test_count;
    }


}