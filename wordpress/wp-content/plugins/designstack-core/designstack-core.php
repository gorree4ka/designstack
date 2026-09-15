<?php
/**
 * Plugin Name: DesignStack Core
 * Description: Модель данных каталога: тип записи «Ресурс», таксономии, поля, блоки и форма «Предложить ресурс». Данные живут здесь, а не в теме.
 * Version: 1.0.0
 * Requires at least: 6.7
 * Requires PHP: 8.3
 * Author: DesignStack
 * Text Domain: designstack-core
 * Domain Path: /languages
 *
 * @package designstack-core
 */

defined( 'ABSPATH' ) || exit;

define( 'DESIGNSTACK_CORE_VERSION', '1.0.0' );
define( 'DESIGNSTACK_CORE_DIR', plugin_dir_path( __FILE__ ) );
define( 'DESIGNSTACK_CORE_URL', plugin_dir_url( __FILE__ ) );

require_once DESIGNSTACK_CORE_DIR . 'includes/enums.php';
require_once DESIGNSTACK_CORE_DIR . 'includes/post-types.php';
require_once DESIGNSTACK_CORE_DIR . 'includes/lessons.php';
require_once DESIGNSTACK_CORE_DIR . 'includes/taxonomies.php';
require_once DESIGNSTACK_CORE_DIR . 'includes/meta.php';
require_once DESIGNSTACK_CORE_DIR . 'includes/rewrite.php';
require_once DESIGNSTACK_CORE_DIR . 'includes/sections.php';
require_once DESIGNSTACK_CORE_DIR . 'includes/filters.php';
require_once DESIGNSTACK_CORE_DIR . 'includes/search.php';
require_once DESIGNSTACK_CORE_DIR . 'includes/render.php';
require_once DESIGNSTACK_CORE_DIR . 'includes/render-page.php';
require_once DESIGNSTACK_CORE_DIR . 'includes/render-home.php';
require_once DESIGNSTACK_CORE_DIR . 'includes/render-entry.php';
require_once DESIGNSTACK_CORE_DIR . 'includes/render-service.php';
require_once DESIGNSTACK_CORE_DIR . 'includes/grade-check.php';
require_once DESIGNSTACK_CORE_DIR . 'includes/blocks.php';
require_once DESIGNSTACK_CORE_DIR . 'includes/form.php';
require_once DESIGNSTACK_CORE_DIR . 'includes/seo.php';
require_once DESIGNSTACK_CORE_DIR . 'includes/schema.php';
require_once DESIGNSTACK_CORE_DIR . 'includes/metrika.php';

if ( is_admin() ) {
	require_once DESIGNSTACK_CORE_DIR . 'admin/meta-box.php';
	require_once DESIGNSTACK_CORE_DIR . 'admin/columns.php';
}

/**
 * Активация: регистрируем типы, заводим термы словаря, обновляем правила адресов.
 *
 * @return void
 */
function designstack_core_activate(): void {
	designstack_core_register_post_type();
	designstack_core_register_lesson();
	designstack_core_register_taxonomies();
	designstack_core_install_terms();
	designstack_core_install_categories();
	designstack_core_register_rewrite_rules();

	// Адрес записи включает раздел: /collections/{slug}/ (карта URL этапа 07, OQ-02 а).
	if ( '/%category%/%postname%/' !== get_option( 'permalink_structure' ) ) {
		update_option( 'permalink_structure', '/%category%/%postname%/' );
	}

	flush_rewrite_rules();
}
register_activation_hook( __FILE__, 'designstack_core_activate' );

/**
 * Деактивация: чистим правила адресов, данные не трогаем.
 *
 * @return void
 */
function designstack_core_deactivate(): void {
	flush_rewrite_rules();
}
register_deactivation_hook( __FILE__, 'designstack_core_deactivate' );
