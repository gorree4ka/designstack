<?php
/**
 * Title: Шапка сайта
 * Slug: designstack/site-header
 * Categories: designstack
 * Inserter: no
 *
 * Семь пунктов меню (brief §6, D35), поиск и переключатель темы. Меню блочной темы — запись `wp_navigation`
 * «Разделы каталога» (scripts/navigation.php), её id ищем по слагу: в `ref` нельзя ставить id классического меню,
 * иначе блок выведет запись с этим номером. Если записи нет, печатаем тот же список ссылок статикой — сайт без
 * навигации не остаётся. До 900 меню сворачивается в кнопку «Меню» через `<details>`, поэтому работает и без
 * JavaScript: без него меню просто раскрыто. Ссылку «Перейти к содержимому» ставит ядро — она ведёт на #ds-main.
 *
 * @package designstack
 */

$ds_items = array(
	'Инструменты' => '/tools/',
	'Учёба'       => '/learn/',
	'Ассеты'      => '/assets/',
	'Сообщества'  => '/community/',
	'Подборки'    => '/collections/',
	'Дайджест'    => '/digest/',
	'О проекте'   => '/about/',
);

$ds_nav = get_posts(
	array(
		'post_type'      => 'wp_navigation',
		'name'           => 'razdely-kataloga',
		'post_status'    => 'publish',
		'posts_per_page' => 1,
	)
);
$ds_ref = $ds_nav ? (int) $ds_nav[0]->ID : 0;

?>
<!-- wp:group {"className":"ds-header","layout":{"type":"constrained"}} -->
<div class="wp-block-group ds-header"><!-- wp:group {"align":"wide","className":"ds-header__bar"} -->
<div class="wp-block-group alignwide ds-header__bar"><!-- wp:html -->
<p class="ds-header__logo"><a href="/"><svg class="ds-header__mark" viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg" fill="currentColor" aria-hidden="true" focusable="false"><polygon points="32,5 56,17 32,29 8,17"/><polygon points="32,20 56,32 32,44 8,32" opacity=".72"/><polygon points="32,35 56,47 32,59 8,47" opacity=".45"/></svg>DesignStack</a></p>
<details class="ds-header__menu" open>
	<summary class="ds-header__menu-toggle ds-button ds-button--icon"><?php echo designstack_icon( 'menu' ); ?><span class="screen-reader-text">Меню</span></summary>
	<?php if ( $ds_ref ) : ?>
	<?php echo do_blocks( '<!-- wp:navigation {"ref":' . $ds_ref . ',"overlayMenu":"never","className":"ds-header__nav"} /-->' ); ?>
	<?php else : ?>
	<nav class="ds-header__nav" aria-label="Разделы каталога">
		<ul>
			<?php foreach ( $ds_items as $ds_title => $ds_url ) : ?>
			<li><a href="<?php echo esc_url( $ds_url ); ?>"><?php echo esc_html( $ds_title ); ?></a></li>
			<?php endforeach; ?>
		</ul>
	</nav>
	<?php endif; ?>
</details>
<?php /* Где у страницы есть своё поле поиска — главная, выдача, 404, — поле в шапке убрано:
   два одинаковых поля в одном экране заставляют выбирать, куда печатать (D43). */ ?>
<?php if ( ! is_front_page() && ! is_search() && ! is_404() ) : ?>
<details class="ds-header__search-menu" open>
	<summary class="ds-header__search-toggle ds-button ds-button--icon"><?php echo designstack_icon( 'search' ); ?><span class="screen-reader-text">Поиск</span></summary>
	<form class="ds-search ds-search--header ds-header__search" role="search" method="get" action="/search/">
		<label class="screen-reader-text" for="ds-header-search">Поиск по каталогу</label>
		<input class="ds-search__field" id="ds-header-search" type="search" name="s" placeholder="Поиск по каталогу">
		<button type="submit" class="ds-button ds-button--secondary">Найти</button>
	</form>
</details>
<?php endif; ?>
<div class="ds-header__controls">
	<button type="button" class="ds-button ds-button--icon ds-theme-toggle" aria-pressed="false"><?php echo designstack_icon( 'moon', '', 'ds-theme-toggle__moon' ); ?><?php echo designstack_icon( 'sun', '', 'ds-theme-toggle__sun' ); ?><span class="screen-reader-text">Тёмная тема</span></button>
</div>
<!-- /wp:html --></div>
<!-- /wp:group --></div>
<!-- /wp:group -->
