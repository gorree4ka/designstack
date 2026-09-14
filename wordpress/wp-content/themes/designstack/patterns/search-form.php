<?php
/**
 * Title: Поиск: в шапке и на главной
 * Slug: designstack/search-form
 * Categories: designstack
 * Inserter: no
 *
 * На главной поля поиска в шапке нет — оно стоит в первом экране (D43). Адрес выдачи — /search/?s= (D36).
 *
 * @package designstack
 */

?>
<!-- wp:html -->
<div class="ds-stack">
	<form class="ds-search ds-search--header" role="search" method="get" action="/search/">
		<label class="screen-reader-text" for="ds-search-header">Поиск по каталогу</label>
		<input class="ds-search__field" id="ds-search-header" type="search" name="s" placeholder="Поиск по каталогу">
		<button type="submit" class="ds-button ds-button--secondary">Найти</button>
	</form>
	<form class="ds-search ds-search--home" role="search" method="get" action="/search/">
		<label class="screen-reader-text" for="ds-search-home">Поиск по каталогу</label>
		<input class="ds-search__field" id="ds-search-home" type="search" name="s" placeholder="Поиск по каталогу">
		<button type="submit" class="ds-button ds-button--primary ds-button--lg">Найти</button>
	</form>
</div>
<!-- /wp:html -->
