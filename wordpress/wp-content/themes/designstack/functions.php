<?php
/**
 * DesignStack: токены дизайн-системы (этап 10) и библиотека паттернов (этап 11).
 *
 * @package designstack
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/**
 * Совпадает ли шаблон текущей страницы с именем.
 *
 * В `_wp_page_template` WordPress хранит слаг без расширения — `page-suggest`, а не
 * `page-suggest.html`. Сравнение с именем файла молча не срабатывает: блок в шаблоне
 * рисуется, а его скрипт не подключается. Проверка: `curl` страницы и поиск имени скрипта.
 *
 * @param string $name Слаг шаблона без расширения.
 * @return bool
 */
function designstack_is_template( string $name ): bool {
	return $name === str_replace( '.html', '', (string) get_page_template_slug() );
}

/**
 * Theme supports.
 */
function designstack_setup() {
	add_theme_support( 'wp-block-styles' );
}
add_action( 'after_setup_theme', 'designstack_setup' );

/**
 * Puts the visitor's theme choice on <html> before the first paint, so a dark page is never drawn light first.
 * Runs first in wp_head, ahead of every stylesheet; the storage key is shared with assets/js/theme-toggle.js.
 */
function designstack_theme_mode_script() {
	wp_print_inline_script_tag(
		"try{var t=localStorage.getItem('designstack-theme');if(t==='dark'||t==='light'){document.documentElement.setAttribute('data-theme',t);}}catch(e){}"
	);
}
add_action( 'wp_head', 'designstack_theme_mode_script', 0 );

/**
 * SVG-фавикон рядом с PNG из настроек WordPress.
 *
 * Вектор не мылится ни на каком экране и меняет цвет под тёмную панель браузера;
 * браузер берёт его, если умеет, иначе остаётся PNG из `site_icon`. Яндекс советует
 * именно SVG или кадр от 120×120 (письмо Вебмастера 16.09.2026).
 *
 * @return void
 */
function designstack_svg_favicon() {
	printf(
		'<link rel="icon" type="image/svg+xml" href="%s" />' . "
",
		esc_url( get_theme_file_uri( 'assets/img/favicon.svg' ) )
	);
}
add_action( 'wp_head', 'designstack_svg_favicon', 2 );

/**
 * Asset version from the file time.
 *
 * @param string $relative Path inside the theme.
 * @return string|null
 */
function designstack_asset_version( $relative ) {
	$path = get_theme_file_path( $relative );

	return file_exists( $path ) ? (string) filemtime( $path ) : null;
}

/**
 * Theme scripts. The grey-box stylesheet left with the stage 08 prototype (stage 13).
 */
function designstack_enqueue_assets() {
	wp_enqueue_script(
		'designstack-header',
		get_theme_file_uri( 'assets/js/header.js' ),
		array(),
		designstack_asset_version( 'assets/js/header.js' ),
		array(
			'strategy'  => 'defer',
			'in_footer' => false,
		)
	);

	wp_enqueue_script(
		'designstack-theme-toggle',
		get_theme_file_uri( 'assets/js/theme-toggle.js' ),
		array(),
		designstack_asset_version( 'assets/js/theme-toggle.js' ),
		array(
			'strategy'  => 'defer',
			'in_footer' => false,
		)
	);

	// Форма «Предложить ресурс»: фокус на сводке ошибок и подпись на время отправки (этап 14).
	// Блок формы стоит в шаблоне страницы, а не в её содержимом, поэтому has_block() его не видит.
	if ( is_singular() && ( has_block( 'designstack/suggest-form' ) || designstack_is_template( 'page-suggest' ) ) ) {
		wp_enqueue_script(
			'designstack-form',
			get_theme_file_uri( 'assets/js/form.js' ),
			array(),
			designstack_asset_version( 'assets/js/form.js' ),
			array(
				'strategy'  => 'defer',
				'in_footer' => true,
			)
		);
	}

	// Тренажёр внутри урока: без скрипта вопросы видны списком, со скриптом идут по одному.
	if ( is_singular( 'lesson' ) ) {
		wp_enqueue_script(
			'designstack-lesson',
			get_theme_file_uri( 'assets/js/lesson.js' ),
			array(),
			designstack_asset_version( 'assets/js/lesson.js' ),
			array(
				'strategy'  => 'defer',
				'in_footer' => true,
			)
		);
	}

	// Живые куски уроков: чек-лист, секундомер молчания, разметка задания, подбор
	// формата, матрица важности, разбор заявок и прикидка объёма. Отдельным файлом от
	// тренажёра: тренажёр есть в каждом уроке, а эти куски — только в своих.
	if ( is_singular( 'lesson' ) ) {
		wp_enqueue_script(
			'designstack-lesson-widgets',
			get_theme_file_uri( 'assets/js/lesson-widgets.js' ),
			array(),
			designstack_asset_version( 'assets/js/lesson-widgets.js' ),
			array(
				'strategy'  => 'defer',
				'in_footer' => true,
			)
		);
	}

	// Память урока: место в тексте, итог тренажёра и отметка «пройден».
	// Отдельным файлом: тренажёр работает и без памяти, а память нужна и там, где тренажёра нет.
	if ( is_singular( 'lesson' ) ) {
		wp_enqueue_script(
			'designstack-lesson-progress',
			get_theme_file_uri( 'assets/js/lesson-progress.js' ),
			array(),
			designstack_asset_version( 'assets/js/lesson-progress.js' ),
			array(
				'strategy'  => 'defer',
				'in_footer' => true,
			)
		);
	}

	// Баннер карты компетенций: знает, проходил ли человек проверку. Ответы лежат
	// в браузере, поэтому состояние баннера подставляет скрипт, а не сервер.
	if ( is_front_page() || has_block( 'designstack/grade-banner' ) ) {
		wp_enqueue_script(
			'designstack-banner',
			get_theme_file_uri( 'assets/js/banner.js' ),
			array(),
			designstack_asset_version( 'assets/js/banner.js' ),
			array(
				'strategy'  => 'defer',
				'in_footer' => true,
			)
		);
	}

	// Карта развития: подставляет ступень человека из ответов проверки и открывает нужный урок.
	if ( is_singular() && ( has_block( 'designstack/skills-map' ) || designstack_is_template( 'page-map' ) ) ) {
		wp_enqueue_script(
			'designstack-map',
			get_theme_file_uri( 'assets/js/map.js' ),
			array(),
			designstack_asset_version( 'assets/js/map.js' ),
			array(
				'strategy'  => 'defer',
				'in_footer' => true,
			)
		);
	}

	// Проверка грейда: пошаговый проход и подсчёт (карта компетенций, D142).
	if ( is_singular() && ( has_block( 'designstack/grade-check' ) || designstack_is_template( 'page-grade-check' ) ) ) {
		wp_enqueue_script(
			'designstack-grade-check',
			get_theme_file_uri( 'assets/js/grade-check.js' ),
			array(),
			designstack_asset_version( 'assets/js/grade-check.js' ),
			array(
				'strategy'  => 'defer',
				'in_footer' => true,
			)
		);
	}

	// Улучшение панели фильтров: короткий адрес, фокус в панели, Escape (этап 14).
	if ( is_tax( array( 'resource_type', 'topic' ) ) ) {
		wp_enqueue_script(
			'designstack-filters',
			get_theme_file_uri( 'assets/js/filters.js' ),
			array(),
			designstack_asset_version( 'assets/js/filters.js' ),
			array(
				'strategy'  => 'defer',
				'in_footer' => true,
			)
		);
	}
}
add_action( 'wp_enqueue_scripts', 'designstack_enqueue_assets' );

/**
 * Dark theme values of the semantic tokens. On the front the file depends on global-styles, so it is printed after
 * the inline global styles and its overrides win; the editor iframe gets global styles from the editor settings,
 * so there the file has no dependency.
 */
function designstack_enqueue_theme_dark() {
	wp_enqueue_style(
		'designstack-theme-dark',
		get_theme_file_uri( 'assets/css/theme-dark.css' ),
		is_admin() ? array() : array( 'global-styles' ),
		designstack_asset_version( 'assets/css/theme-dark.css' )
	);
}
add_action( 'wp_enqueue_scripts', 'designstack_enqueue_theme_dark', 20 );
add_action( 'enqueue_block_assets', 'designstack_enqueue_theme_dark' );

/**
 * Pattern library stylesheet (directive 11). Stands after the global styles, so a pattern rule beats a preset default
 * but never the dark theme values: those live on :root and are read through var().
 */
function designstack_enqueue_patterns() {
	wp_enqueue_style(
		'designstack-patterns',
		get_theme_file_uri( 'assets/css/patterns.css' ),
		is_admin() ? array() : array( 'global-styles' ),
		designstack_asset_version( 'assets/css/patterns.css' )
	);
}
add_action( 'wp_enqueue_scripts', 'designstack_enqueue_patterns', 21 );
add_action( 'enqueue_block_assets', 'designstack_enqueue_patterns' );

/**
 * Styleguide page assets: the grid of the showcase and the «highlight what is clickable» toggle.
 */
function designstack_enqueue_styleguide() {
	if ( ! is_page( 'styleguide' ) ) {
		return;
	}

	wp_enqueue_style(
		'designstack-styleguide',
		get_theme_file_uri( 'assets/css/styleguide.css' ),
		array( 'designstack-patterns' ),
		designstack_asset_version( 'assets/css/styleguide.css' )
	);

	wp_enqueue_script(
		'designstack-styleguide',
		get_theme_file_uri( 'assets/js/styleguide.js' ),
		array(),
		designstack_asset_version( 'assets/js/styleguide.js' ),
		array(
			'strategy'  => 'defer',
			'in_footer' => true,
		)
	);
}
add_action( 'wp_enqueue_scripts', 'designstack_enqueue_styleguide', 22 );

/**
 * Pattern categories: one for the site patterns a curator inserts, one hidden for the showcase wrappers.
 */
function designstack_register_pattern_categories() {
	register_block_pattern_category( 'designstack', array( 'label' => __( 'DesignStack', 'designstack' ) ) );
	register_block_pattern_category( 'designstack-styleguide', array( 'label' => __( 'DesignStack: витрина', 'designstack' ) ) );
}
add_action( 'init', 'designstack_register_pattern_categories' );

/**
 * Block styles of the library. Ghost buttons are not registered on purpose: by D50 a button always has a border
 * or a fill, so «quiet» buttons in the header are outline squares with an icon.
 */
function designstack_register_block_styles() {
	register_block_style( 'core/button', array( 'name' => 'secondary', 'label' => __( 'Контурная', 'designstack' ) ) );
	register_block_style( 'core/group', array( 'name' => 'card', 'label' => __( 'Карточка', 'designstack' ) ) );
	register_block_style( 'core/group', array( 'name' => 'panel', 'label' => __( 'Панель', 'designstack' ) ) );
	register_block_style( 'core/paragraph', array( 'name' => 'meta', 'label' => __( 'Мета', 'designstack' ) ) );
}
add_action( 'init', 'designstack_register_block_styles' );

/**
 * Lucide icon from the theme sprite.
 *
 * @param string $name  Icon name from assets/img/icons.svg.
 * @param string $label Visible-to-screen-readers label; empty makes the icon decorative.
 * @return string
 */
function designstack_icon( $name, $label = '', $classes = '' ) {
	$icons = array( 'circle-check', 'triangle-alert', 'circle-x', 'clock', 'info', 'search', 'menu', 'x', 'moon', 'chevron-left', 'chevron-right', 'external-link', 'sun' );

	if ( ! in_array( $name, $icons, true ) ) {
		return '';
	}

	$a11y = '' === $label
		? ' aria-hidden="true"'
		: ' role="img" aria-label="' . esc_attr( $label ) . '"';

	return sprintf(
		'<svg class="ds-icon%4$s"%1$s><use href="%2$s#icon-%3$s"></use></svg>',
		$a11y,
		esc_url( get_theme_file_uri( 'assets/img/icons.svg' ) ),
		esc_attr( $name ),
		'' === $classes ? '' : ' ' . esc_attr( $classes )
	);
}

/**
 * Inline illustration of an empty state: its colours come from the token variables, so one file works in both themes.
 *
 * @param string $name Illustration name without the extension.
 * @return string
 */
function designstack_illustration( $name ) {
	$allowed = array( 'empty-filters', 'empty-section', 'not-found' );

	if ( ! in_array( $name, $allowed, true ) ) {
		return '';
	}

	$path = get_theme_file_path( 'assets/img/' . $name . '.svg' );

	return file_exists( $path ) ? file_get_contents( $path ) : ''; // phpcs:ignore WordPress.WP.AlternativeFunctions.file_get_contents_file_get_contents
}

/**
 * Core breadcrumbs carry our word for the landmark: the dictionary says «Навигационная цепочка».
 *
 * @param string $content Rendered block.
 * @return string
 */
function designstack_breadcrumbs_markup( $content ) {
	$content = preg_replace(
		'/aria-label="[^"]*"/',
		'aria-label="' . esc_attr__( 'Навигационная цепочка', 'designstack' ) . '"',
		$content,
		1
	);

	// Разделитель рисует паттерн (`›` через ::before). Свой разделитель ядра гасим,
	// иначе на странице стоят два подряд: «Главная / › Инструменты».
	return preg_replace( '/--separator: &quot;[^&]*&quot;/', '--separator: &quot;&quot;', $content, 1 );
}
add_filter( 'render_block_core/breadcrumbs', 'designstack_breadcrumbs_markup' );

/**
 * Current section in the menu.
 *
 * Core marks a navigation link current only for a matched post ID or a post type archive.
 * Catalogue sections are custom links (`/tools/`, `/collections/`), so the theme marks them:
 * a section stays current on its archive and on the records inside it.
 *
 * @return string URL of the current section or ''.
 */
function designstack_current_section_url() {
	if ( is_tax( 'resource_type' ) ) {
		$term = get_queried_object();

		return $term instanceof WP_Term ? (string) get_term_link( $term ) : '';
	}

	if ( is_singular( 'resource' ) ) {
		$terms = get_the_terms( get_queried_object_id(), 'resource_type' );

		return $terms && ! is_wp_error( $terms ) ? (string) get_term_link( $terms[0] ) : '';
	}

	if ( is_category() ) {
		$term = get_queried_object();

		return $term instanceof WP_Term ? (string) get_term_link( $term ) : '';
	}

	if ( is_singular( 'post' ) ) {
		$terms = get_the_category( get_queried_object_id() );

		return $terms ? (string) get_category_link( $terms[0] ) : '';
	}

	if ( is_page() ) {
		return (string) get_permalink( get_queried_object_id() );
	}

	return '';
}

/**
 * Marks the current menu item.
 *
 * @param string $content Rendered block.
 * @param array  $block   Parsed block.
 * @return string
 */
function designstack_navigation_current( $content, $block ) {
	$url = isset( $block['attrs']['url'] ) ? (string) $block['attrs']['url'] : '';
	$now = designstack_current_section_url();

	if ( '' === $url || '' === $now || untrailingslashit( $url ) !== untrailingslashit( $now ) ) {
		return $content;
	}

	$tags = new WP_HTML_Tag_Processor( $content );

	if ( $tags->next_tag( 'li' ) ) {
		$tags->add_class( 'current-menu-item' );
	}

	if ( $tags->next_tag( 'a' ) ) {
		$tags->set_attribute( 'aria-current', 'page' );
	}

	return $tags->get_updated_html();
}
add_filter( 'render_block_core/navigation-link', 'designstack_navigation_current', 10, 2 );

/**
 * The showcase is a service page: out of search results.
 *
 * @param array $robots Robots directives.
 * @return array
 */
function designstack_styleguide_robots( $robots ) {
	if ( is_page( 'styleguide' ) ) {
		$robots['noindex']  = true;
		$robots['nofollow'] = true;
	}

	return $robots;
}
add_filter( 'wp_robots', 'designstack_styleguide_robots' );

/**
 * The showcase stays out of search results too.
 *
 * It is a service page with noindex and no place in the sitemap, so it has nothing
 * to do in the results next to catalogue resources.
 *
 * @param WP_Query $query Query.
 * @return void
 */
function designstack_search_skip_styleguide( $query ) {
	if ( is_admin() || ! $query->is_main_query() || ! $query->is_search() ) {
		return;
	}

	$page = get_page_by_path( 'styleguide' );

	if ( $page ) {
		$query->set( 'post__not_in', array_merge( (array) $query->get( 'post__not_in' ), array( $page->ID ) ) );
	}
}
add_action( 'pre_get_posts', 'designstack_search_skip_styleguide' );

/**
 * Link to the showcase for the editor: in the admin bar, not on the site.
 *
 * @param WP_Admin_Bar $bar Admin bar.
 */
function designstack_admin_bar_styleguide( $bar ) {
	$bar->add_node(
		array(
			'id'    => 'designstack-styleguide',
			'title' => __( 'Витрина', 'designstack' ),
			'href'  => home_url( '/styleguide/' ),
		)
	);
}
add_action( 'admin_bar_menu', 'designstack_admin_bar_styleguide', 80 );

/**
 * Showcase cell: renders the real pattern and puts a state class on its root elements, so the grid of states
 * never becomes a copy of the markup (directive 11, «Грабли»).
 *
 * @param string $slug   Pattern slug without the namespace.
 * @param string $target Class of the elements that get the state.
 * @param string $state  State class, for example is-hover.
 * @return string
 */
function designstack_styleguide_pattern( $slug, $target = '', $state = '', $strip_ids = false ) {
	$html = do_blocks( '<!-- wp:pattern {"slug":"designstack/' . $slug . '"} /-->' );

	if ( ( '' === $state || '' === $target ) && ! $strip_ids ) {
		return $html;
	}

	$processor = new WP_HTML_Tag_Processor( $html );
	while ( $processor->next_tag() ) {
		if ( '' !== $state && '' !== $target && $processor->has_class( $target ) ) {
			$processor->add_class( $state );
		}

		// Паттерн, показанный на витрине несколько раз, не должен плодить одинаковые id.
		if ( $strip_ids ) {
			$processor->remove_attribute( 'id' );
			$processor->remove_attribute( 'for' );
		}
	}

	return $processor->get_updated_html();
}

/**
 * Matrix of one pattern: a cell per state, each cell rendering the same pattern.
 *
 * @param string $slug   Pattern slug.
 * @param string $target Class of the elements that get the state.
 * @param array  $states Map of state class to caption; an empty key means the default state.
 * @return string
 */
function designstack_styleguide_matrix( $slug, $target, $states ) {
	$cells = '';
	foreach ( $states as $state => $caption ) {
		$cells .= '<div class="sg-cell"><p class="sg-cell__label">' . esc_html( $caption ) . '</p><div class="sg-cell__body">'
			. designstack_styleguide_pattern( $slug, $target, (string) $state )
			. '</div></div>';
	}

	return '<div class="sg-matrix">' . $cells . '</div>';
}
