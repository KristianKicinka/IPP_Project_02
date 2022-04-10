<?php

class Script{

    private bool $recursive = false;
    private bool $parse_tests = true;
    private bool $int_tests = true;
    private bool $noclean = false;

    private $directory_path = null;
    private $jexam_path = null;
    private $parse_script_file = null;
    private $int_script_file = null;

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
    public function isNoclean(): bool
    {
        return $this->noclean;
    }

    /**
     * @param bool $noclean
     */
    public function setNoclean(bool $noclean): void
    {
        $this->noclean = $noclean;
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
        $file = fopen($parse_script_file, "r") or close_script(FILE_ERROR);
        $this->parse_script_file = $file;
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
        $file = fopen($int_script_file, "r") or close_script(FILE_ERROR);
        $this->int_script_file = $file;
    }




}