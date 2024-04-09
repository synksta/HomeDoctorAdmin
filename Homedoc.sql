PGDMP  1                     |         
   HomeDoctor    16.1    16.0     �           0    0    ENCODING    ENCODING        SET client_encoding = 'UTF8';
                      false            �           0    0 
   STDSTRINGS 
   STDSTRINGS     (   SET standard_conforming_strings = 'on';
                      false            �           0    0 
   SEARCHPATH 
   SEARCHPATH     8   SELECT pg_catalog.set_config('search_path', '', false);
                      false            �           1262    16472 
   HomeDoctor    DATABASE     �   CREATE DATABASE "HomeDoctor" WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE_PROVIDER = libc LOCALE = 'Russian_Russia.1251';
    DROP DATABASE "HomeDoctor";
                postgres    false            �            1259    16478    keywords    TABLE     _   CREATE TABLE public.keywords (
    id integer NOT NULL,
    word character varying NOT NULL
);
    DROP TABLE public.keywords;
       public         heap    postgres    false            �           0    0    TABLE keywords    COMMENT     N   COMMENT ON TABLE public.keywords IS 'The table containing all the keywords.';
          public          postgres    false    216            �            1259    16515    keywords__id_seq    SEQUENCE     �   ALTER TABLE public.keywords ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.keywords__id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
            public          postgres    false    216            �            1259    16485    ref_keywords    TABLE     a   CREATE TABLE public.ref_keywords (
    symptom integer NOT NULL,
    keyword integer NOT NULL
);
     DROP TABLE public.ref_keywords;
       public         heap    postgres    false            �           0    0    TABLE ref_keywords    COMMENT     u   COMMENT ON TABLE public.ref_keywords IS 'The reference table binding keywords collection to the specific symptoms.';
          public          postgres    false    217            �            1259    16473    symptoms    TABLE     �   CREATE TABLE public.symptoms (
    id integer NOT NULL,
    name character varying NOT NULL,
    description character varying,
    page integer,
    yes integer,
    no integer
);
    DROP TABLE public.symptoms;
       public         heap    postgres    false            �           0    0    TABLE symptoms    COMMENT     m   COMMENT ON TABLE public.symptoms IS 'Main table containing all the symptoms, architecturally it''s a tree.';
          public          postgres    false    215            �            1259    16514    symptoms__id_seq    SEQUENCE     �   ALTER TABLE public.symptoms ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.symptoms__id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
            public          postgres    false    215            �            1259    16526    users    TABLE     t   CREATE TABLE public.users (
    name character varying(30) NOT NULL,
    password character varying(30) NOT NULL
);
    DROP TABLE public.users;
       public         heap    postgres    false            �          0    16478    keywords 
   TABLE DATA           ,   COPY public.keywords (id, word) FROM stdin;
    public          postgres    false    216   [        �          0    16485    ref_keywords 
   TABLE DATA           8   COPY public.ref_keywords (symptom, keyword) FROM stdin;
    public          postgres    false    217   �!       �          0    16473    symptoms 
   TABLE DATA           H   COPY public.symptoms (id, name, description, page, yes, no) FROM stdin;
    public          postgres    false    215   �!       �          0    16526    users 
   TABLE DATA           /   COPY public.users (name, password) FROM stdin;
    public          postgres    false    220   �&       �           0    0    keywords__id_seq    SEQUENCE SET     ?   SELECT pg_catalog.setval('public.keywords__id_seq', 46, true);
          public          postgres    false    219            �           0    0    symptoms__id_seq    SEQUENCE SET     ?   SELECT pg_catalog.setval('public.symptoms__id_seq', 46, true);
          public          postgres    false    218            *           2606    16484    keywords keywords_pkey 
   CONSTRAINT     T   ALTER TABLE ONLY public.keywords
    ADD CONSTRAINT keywords_pkey PRIMARY KEY (id);
 @   ALTER TABLE ONLY public.keywords DROP CONSTRAINT keywords_pkey;
       public            postgres    false    216            ,           2606    16493    ref_keywords ref_keywords_pkey 
   CONSTRAINT     j   ALTER TABLE ONLY public.ref_keywords
    ADD CONSTRAINT ref_keywords_pkey PRIMARY KEY (symptom, keyword);
 H   ALTER TABLE ONLY public.ref_keywords DROP CONSTRAINT ref_keywords_pkey;
       public            postgres    false    217    217            (           2606    16491    symptoms symptoms_pkey 
   CONSTRAINT     T   ALTER TABLE ONLY public.symptoms
    ADD CONSTRAINT symptoms_pkey PRIMARY KEY (id);
 @   ALTER TABLE ONLY public.symptoms DROP CONSTRAINT symptoms_pkey;
       public            postgres    false    215            .           2606    16530    users users_pkey 
   CONSTRAINT     P   ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (name);
 :   ALTER TABLE ONLY public.users DROP CONSTRAINT users_pkey;
       public            postgres    false    220            1           2606    16521    ref_keywords keyword_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.ref_keywords
    ADD CONSTRAINT keyword_fkey FOREIGN KEY (keyword) REFERENCES public.keywords(id) NOT VALID;
 C   ALTER TABLE ONLY public.ref_keywords DROP CONSTRAINT keyword_fkey;
       public          postgres    false    4650    217    216            �           0    0 '   CONSTRAINT keyword_fkey ON ref_keywords    COMMENT     S   COMMENT ON CONSTRAINT keyword_fkey ON public.ref_keywords IS 'Keyword''s ref id.';
          public          postgres    false    4657            /           2606    16509    symptoms no_fkey    FK CONSTRAINT     w   ALTER TABLE ONLY public.symptoms
    ADD CONSTRAINT no_fkey FOREIGN KEY (no) REFERENCES public.symptoms(id) NOT VALID;
 :   ALTER TABLE ONLY public.symptoms DROP CONSTRAINT no_fkey;
       public          postgres    false    215    4648    215            �           0    0    CONSTRAINT no_fkey ON symptoms    COMMENT     M   COMMENT ON CONSTRAINT no_fkey ON public.symptoms IS '''No'' symptom''s id.';
          public          postgres    false    4655            2           2606    16516    ref_keywords symptom_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.ref_keywords
    ADD CONSTRAINT symptom_fkey FOREIGN KEY (symptom) REFERENCES public.symptoms(id) NOT VALID;
 C   ALTER TABLE ONLY public.ref_keywords DROP CONSTRAINT symptom_fkey;
       public          postgres    false    215    217    4648            �           0    0 '   CONSTRAINT symptom_fkey ON ref_keywords    COMMENT     S   COMMENT ON CONSTRAINT symptom_fkey ON public.ref_keywords IS 'Symptom''s ref id.';
          public          postgres    false    4658            0           2606    16504    symptoms yes_fkey    FK CONSTRAINT     y   ALTER TABLE ONLY public.symptoms
    ADD CONSTRAINT yes_fkey FOREIGN KEY (yes) REFERENCES public.symptoms(id) NOT VALID;
 ;   ALTER TABLE ONLY public.symptoms DROP CONSTRAINT yes_fkey;
       public          postgres    false    215    215    4648            �           0    0    CONSTRAINT yes_fkey ON symptoms    COMMENT     O   COMMENT ON CONSTRAINT yes_fkey ON public.symptoms IS '''Yes'' symptom''s id.';
          public          postgres    false    4656            �   ;  x�UQ[N�@��O� ��i�]8L�JR+"��WHK^��`߈��H6�=3�YG�"�tRs�%y֝4R�'=�V�%�|ʠG��kNW$' /z��IwZJ\�?#�9᫕��C����Q;����tإ�
�L "���0I�o0xc��V�{����FFvE��">#p��g2���=��j#�=����0�J��LѸO��Ǝ!>���ώ�F�\x�?��k�\sc�[�z��,ρ�4�l�J+��ub���j��F�HoN1��rO`
���@��*�M�䰊Wg��a�o(mFE      �      x�36�42����� 
a�      �     x��VmR�F�-�b��,fȟ� '��Xv�p�B�V���n�?�W	Y��0s��$��FblXHj��4�y��ߛ�7�����w~�K����������:�����.L���bɅ��-��a�}��~�W2�a����	�e�/����S��8wt�p`�kwt�������h�&��#������gxm~J�*o�����Q��!�/������Ɨ���y�MG�k&�5��ؤ��p	"��@a��9b���	,��@�s �D%v5�W�b��C��Z_�����j��G�8�	vgN�l����M|����tm�]��+��L��t8�a1A��a�\��.%f��ˆ�@��:5���p��l�@.�X���X��'�h�Ă �,7HE� �E����3}�doM�Ǣ�b���	^&;�f��K ΂��j�e5�|y�0h�dLM�࠾ >��
6ɜm����$]iH_6tQ#�s�� 㙌ݲ.�<�w�m��H}�=�?Z������7��U)�qf�2�X�,w!P+&���>���|��bX
�����/ʝ��w4C=ݲ�,���7��	�:�* ����N!�Kb8��̫V��Y�V�\�DQ6<�uP[����{"+��*��	�N��%_�bI����(�X��0M���R��]�犕�vA܃D8'O��R��_�}�P���a����^�@�:��aZU�p)0��@�s�#�r�,ZK�ZT�p-�_%~'J�/-�I���^�Q����z���}O�/,�FA�ªzr͌쥕�J��V�߈��y�h˔ԏѓ.�6䤵���*^Ȅ����� ��"�5X�(]q�\�-ǰ��ל�,����X�é�ow5(��RV	�&1�Ũ7��3�J3��������x̥�S�!*��b{��Ο�ʦj�'ީ��Qtݼc�p&�[�bY-��V����.��\z���7��B�<�-��ѳL�jQm��6�tU��������i�mVm�C6�9V�zz��%��������˝NT�]���'����k�8^w"���؆@�_�4�T�Hu/2J=v1_��I�tP�f�O�$i�V!��$�0�L�l�R[à:������)����"����"�]$ZL�����,�--�d��$a�(�3����7�*, �gU��
2��n��u����_��8�`aJ���*"�^���S��?E@��0���s�J�tN�o��삪R���Aue<�[2^� 웱�#-�ѐkڴ���?�Xn�开m�2KIuw�?{�~x����a�g�ٽz{���h4�#�      �   0   x�-N-2�H,..�/J1�
��|c0��7�(0��p��qqq J��     