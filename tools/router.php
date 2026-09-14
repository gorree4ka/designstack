<?php
/**
 * Router for PHP built-in server (php -S) so that WordPress pretty permalinks work.
 * Serves existing files directly, otherwise hands the request to index.php.
 */
$root = __DIR__ . '/../wordpress';
$path = parse_url( $_SERVER['REQUEST_URI'], PHP_URL_PATH );
$file = realpath( $root . $path );
if ( $file && strpos( $file, realpath( $root ) ) === 0 ) {
	if ( is_dir( $file ) && file_exists( $file . '/index.php' ) ) {
		$_SERVER['SCRIPT_NAME'] = rtrim( $path, '/' ) . '/index.php';
		chdir( $file );
		require $file . '/index.php';
		return true;
	}
	if ( is_file( $file ) ) {
		return false; // static file or explicit .php — let the server handle it
	}
}
$_SERVER['SCRIPT_NAME'] = '/index.php';
chdir( $root );
require $root . '/index.php';
