<?php

class TestObject{

    private String $test_name;
    private String $test_directory_path;
    private String $test_file_path;

    private bool $src_file;
    private bool $out_file;
    private bool $in_file;
    private bool $rc_file;

    private int $entered_exit_code;
    private int $expected_exit_code;

    private String $tmp_out_file_path;
    private String $tmp_err_file_path;

    private bool $same_output;

    public function __construct($test_name, $test_directory_path, $test_file_path){
        $this->test_name = $test_name;
        $this->test_directory_path = $test_directory_path;
        $this->test_file_path = $test_file_path;

        $this->src_file = false;
        $this->out_file = false;
        $this->in_file = false;
        $this->rc_file = false;

        $this->entered_exit_code = -1;
        $this->expected_exit_code = -1;
        $this->tmp_err_file_path = "";
        $this->tmp_out_file_path = "";
        $this->same_output = false;

    }

    /**
     * @return String
     */
    public function getTestName(): string
    {
        return $this->test_name;
    }

    /**
     * @param String $test_name
     */
    public function setTestName(string $test_name): void
    {
        $this->test_name = $test_name;
    }

    /**
     * @return String
     */
    public function getTestDirectoryPath(): string
    {
        return $this->test_directory_path;
    }

    /**
     * @param String $test_directory_path
     */
    public function setTestDirectoryPath(string $test_directory_path): void
    {
        $this->test_directory_path = $test_directory_path;
    }

    /**
     * @return String
     */
    public function getTestFilePath(): string
    {
        return $this->test_file_path;
    }

    /**
     * @param String $test_file_path
     */
    public function setTestFilePath(string $test_file_path): void
    {
        $this->test_file_path = $test_file_path;
    }

    /**
     * @return bool
     */
    public function isSrcFile(): bool
    {
        return $this->src_file;
    }

    /**
     * @param bool $src_file
     */
    public function setSrcFile(bool $src_file): void
    {
        $this->src_file = $src_file;
    }

    /**
     * @return bool
     */
    public function isOutFile(): bool
    {
        return $this->out_file;
    }

    /**
     * @param bool $out_file
     */
    public function setOutFile(bool $out_file): void
    {
        $this->out_file = $out_file;
    }

    /**
     * @return bool
     */
    public function isInFile(): bool
    {
        return $this->in_file;
    }

    /**
     * @param bool $in_file
     */
    public function setInFile(bool $in_file): void
    {
        $this->in_file = $in_file;
    }

    /**
     * @return bool
     */
    public function isRcFile(): bool
    {
        return $this->rc_file;
    }

    /**
     * @param bool $rc_file
     */
    public function setRcFile(bool $rc_file): void
    {
        $this->rc_file = $rc_file;
    }

    /**
     * @return int
     */
    public function getEnteredExitCode(): int
    {
        return $this->entered_exit_code;
    }

    /**
     * @param int $entered_exit_code
     */
    public function setEnteredExitCode(int $entered_exit_code): void
    {
        $this->entered_exit_code = $entered_exit_code;
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
     * @return String|null
     */
    public function getTmpOutFilePath(): ?string
    {
        return $this->tmp_out_file_path;
    }

    /**
     * @param String|null $tmp_out_file_path
     */
    public function setTmpOutFilePath(?string $tmp_out_file_path): void
    {
        $this->tmp_out_file_path = $tmp_out_file_path;
    }

    /**
     * @return String|null
     */
    public function getTmpErrFilePath(): ?string
    {
        return $this->tmp_err_file_path;
    }

    /**
     * @param String|null $tmp_err_file_path
     */
    public function setTmpErrFilePath(?string $tmp_err_file_path): void
    {
        $this->tmp_err_file_path = $tmp_err_file_path;
    }

    /**
     * @return bool
     */
    public function isSameOutput(): bool
    {
        return $this->same_output;
    }

    /**
     * @param bool $same_output
     */
    public function setSameOutput(bool $same_output): void
    {
        $this->same_output = $same_output;
    }

}