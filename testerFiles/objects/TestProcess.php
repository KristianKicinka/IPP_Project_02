<?php

/***
 * Projekt : IPP projekt, časť č.2 (Test PHP 8.1)
 * @file TestProcess.php
 * @author Kristián Kičinka (xkicin02)
 */

namespace objects;
class TestProcess
{
    private string $type;
    private string $name;
    private string $testing_file;

    private int $returned_exit_code;
    private int $expected_exit_code;

    private string $tmp_out_file_path;
    private string $tmp_err_file_path;

    private bool $test_passed;

    /**
     * @param String $type
     * @param String $name
     * @param String $testing_file
     */
    public function __construct(string $type, string $name, string $testing_file)
    {
        $this->type = $type;
        $this->name = $name;
        $this->testing_file = $testing_file;
    }

    /**
     * @return String
     */
    public function getType(): string
    {
        return $this->type;
    }

    /**
     * @param String $type
     */
    public function setType(string $type): void
    {
        $this->type = $type;
    }

    /**
     * @return String
     */
    public function getName(): string
    {
        return $this->name;
    }

    /**
     * @param String $name
     */
    public function setName(string $name): void
    {
        $this->name = $name;
    }

    /**
     * @return String
     */
    public function getTestingFile(): string
    {
        return $this->testing_file;
    }

    /**
     * @param String $testing_file
     */
    public function setTestingFile(string $testing_file): void
    {
        $this->testing_file = $testing_file;
    }

    /**
     * @return int
     */
    public function getReturnedExitCode(): int
    {
        return $this->returned_exit_code;
    }

    /**
     * @param int $returned_exit_code
     */
    public function setReturnedExitCode(int $returned_exit_code): void
    {
        $this->returned_exit_code = $returned_exit_code;
    }

    /**
     * @return int
     */
    public function getExpectedExitCode(): int
    {
        return $this->expected_exit_code;
    }

    /**
     * @param int $expected_exit_code
     */
    public function setExpectedExitCode(int $expected_exit_code): void
    {
        $this->expected_exit_code = $expected_exit_code;
    }

    /**
     * @return String
     */
    public function getTmpOutFilePath(): string
    {
        return $this->tmp_out_file_path;
    }

    /**
     * @param String $tmp_out_file_path
     */
    public function setTmpOutFilePath(string $tmp_out_file_path): void
    {
        $this->tmp_out_file_path = $tmp_out_file_path;
    }

    /**
     * @return String
     */
    public function getTmpErrFilePath(): string
    {
        return $this->tmp_err_file_path;
    }

    /**
     * @param String $tmp_err_file_path
     */
    public function setTmpErrFilePath(string $tmp_err_file_path): void
    {
        $this->tmp_err_file_path = $tmp_err_file_path;
    }

    /**
     * @return bool
     */
    public function isTestPassed(): bool
    {
        return $this->test_passed;
    }

    /**
     * @param bool $test_passed
     */
    public function setTestPassed(bool $test_passed): void
    {
        $this->test_passed = $test_passed;
    }


}